/**
    MyMiddleware.java
    21-10-2017

    @Description: Class implementing the middleware. The middleware will connect to up to 3 Memcached servers on the backend to retrieve information stored on them. On the front end, it will listen to client requests to for load balanced and forwarded to the server. This will run a net-thread to listen for requests from clients and then pass those to a queue. Note that this class also spawns the worker threads on initialisation. This class should be called from RunMW.
    @Author: Jakob Beckmann
*/

package asl_project;

import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.net.InetSocketAddress;
import java.io.IOException;
import java.util.concurrent.*;
import java.util.logging.*;
import java.io.PrintWriter;
import java.io.FileWriter;

import asl_project.util.*;
import asl_project.logging.*;

/**
    Class representing the middleware. Instantiating this class will create worker threads and a socket listening for clients. However, run() must be called before any client requests will be accepted.
*/
public class MyMiddleware {
    // Logging
    private static final Logger SYS_LOG = Logger.getLogger("System");
    private static final Logger ANA_LOG = Logger.getLogger("Analysis");
    private String home;
    private static final ScheduledExecutorService ses = Executors.newSingleThreadScheduledExecutor();

    // Private fields
    private Selector selector;
    private ServerSocketChannel serverChannel;
    private ExecutorService threadPool;
    private BlockingQueue<Request> queue;
    private ArrayList<Worker> workers;
    private long timeRun;


    /**
        Constructor.
        @param myIP: String of the local IP address the listener socket should listen to.
        @param port: Integer of the port the listener socket listens to.
        @param mcAddresses: List of strings containing the addresses and ports of the memcached servers.
        @param numThreadsPTP: Integer representing the number of worker threads this middleware should utilise.
        @param readSharded: Boolean for read sharding. If this is true, GET requests containing serveral keys will be split into smaller requests accross the servers.
    */
    public MyMiddleware(String myIP, int port, List<String> mcAddresses, int numThreadsPTP, boolean readSharded) {
        // The buffer needs to be large enough to contain up to 10 * 250 byte keys and 1k bytes of data
        this.timeRun = - System.nanoTime() >> 10;                   // In microseconds
        this.workers = new ArrayList<Worker>();
        this.queue = new LinkedBlockingQueue<Request>();
        home = System.getProperty("user.home");

        // ===========================================================================
        // LOGGING
        // ===========================================================================

        // Set up the system logger for system critical information
        try {
            FileHandler fh = new FileHandler(home + "/system_report.log", true);
            fh.setFormatter(new SysFormatter());
            SYS_LOG.addHandler(fh);
            SYS_LOG.setUseParentHandlers(false);
            SYS_LOG.setLevel(Level.CONFIG);
            SYS_LOG.info(String.format("\n\n%60s\n\n", "Middleware booting."));
        } catch(IOException ex) {
            System.out.println("Could not set up the system logger:\n" + ex);
            System.exit(1);
        }

        // Set up logger for system analysis
        try {
            FileHandler fh = new FileHandler(home + "/analysis.log", true);
            ConsoleHandler ch = new ConsoleHandler();
            fh.setFormatter(new AnaFormatter());
            ch.setFormatter(new ConFormatter());
            ANA_LOG.addHandler(fh);
            ANA_LOG.addHandler(ch);
            ANA_LOG.setUseParentHandlers(false);
            ANA_LOG.setLevel(Level.FINEST);
        } catch(IOException ex) {
            SYS_LOG.severe("Could not set up data logger. Terminating ...");
            System.exit(1);
        }
        ANA_LOG.info(String.format("Threads: %d, Sharded reads: %b, Number of Memcached servers: %d.\n", numThreadsPTP, readSharded, mcAddresses.size()));
        ANA_LOG.info("All measures in microseconds.");
        ANA_LOG.info(Worker.initLog());




        // ===========================================================================
        // CLIENT LISTENING AND THREAD POOL
        // ===========================================================================

        // Set up the selector to listen to the incoming client requests
        try {
            this.selector = Selector.open();
            // Create a server socket channel listening for new clients
            this.serverChannel = ServerSocketChannel.open();
            this.serverChannel.socket().bind(new InetSocketAddress(myIP, port));
            this.serverChannel.configureBlocking(false);
            SelectionKey key = serverChannel.register(selector, SelectionKey.OP_ACCEPT);
        } catch(IOException ex) {
            SYS_LOG.warning("Could not set up the ServerSocketChannel. Terminating ...");
            System.exit(1);
        }

        // Create a thread pool executor of fixed size
        this.threadPool = Executors.newFixedThreadPool(numThreadsPTP);
        // Launch worker threads
        for(int threadID = 0; threadID < numThreadsPTP; threadID++) {
            workers.add(new Worker(queue, threadID, mcAddresses, readSharded));
            this.threadPool.execute(workers.get(threadID));
        }
        SYS_LOG.info(String.format("Middleware finished booting with %d threads.", numThreadsPTP));


        // ===========================================================================
        // LOG FLUSHING
        // ===========================================================================

        // Set up the scheduling for flushing the data buffer from data.
        MyMiddleware.ses.scheduleWithFixedDelay(new LoggerRunnable(this), 1, 1, TimeUnit.SECONDS);
    }


    /**
        Runs the middleware. This it the net-thread listening to client requests. This is also where the sutdown hook is implemented to catch shutdown signals from the OS. If such a signal is caught, the middleware stops the executor hence interrupting worker threads and tries to close all connections.
    */
    public void run() {
        // Add shutdown hook for interruption signals
        Runtime.getRuntime().addShutdownHook(new ShutDown(this));

        // Perform the work for the net thread
        while(true) {
            // Get the keys in the selected-set of the selector
            try {
                selector.select();
            } catch(IOException ex) {
                SYS_LOG.info("Selector selected-set could not be updated.");
            }

            Iterator<SelectionKey> iterator = selector.selectedKeys().iterator();
            while(iterator.hasNext()) {
                SelectionKey key = iterator.next();
                iterator.remove();
                if(key.isAcceptable()) {
                    // New client requested a connection
                    try {
                        SocketChannel channel = serverChannel.accept();
                        channel.configureBlocking(false);
                        SelectionKey newKey = channel.register(selector, SelectionKey.OP_READ);
                        SYS_LOG.info("New client added to the selector.");
                    } catch(ClosedChannelException ex) {
                        SYS_LOG.info("Client closed the connection before he could be added to the selector.");
                    } catch(IOException ex) {
                        SYS_LOG.warning("Failure to open a new channel for a client.");
                    }
                } else if(key.isReadable()) {
                    // Create a ByteBuffer to read data from client
                    ByteBuffer buffer = ByteBuffer.allocate(4096);

                    // Read from the channel
                    SocketChannel channel = (SocketChannel) key.channel();
                    int bytesRead;
                    try {
                        bytesRead = channel.read(buffer);
                    } catch(IOException ex) {
                        SYS_LOG.info("Could not read request from client. Dropping request.");
                        continue;
                    }

                    // Check if the client wants to close the connection
                    if(bytesRead == -1) {
                        SYS_LOG.info("Client requested connection closure.");
                        try {
                            key.channel().close();
                        } catch(IOException ex) {
                            SYS_LOG.info("Could not close channel after client request connection closure.");
                        }
                        key.cancel();
                        continue;
                    }
                    queue.offer(new Request(buffer, key));
                } else {
                    SYS_LOG.warning("Invalid SelectionKey in selection-set.");
                }
            }
        }
    }


    /**
        Class LoggerRunnable implementing Runnable. This should be launched in an executor service to log data to the screen. Depending on what interval the run method is called, the logger will print to command line and log file data collected during the calling intervals.
    */
    private class LoggerRunnable implements Runnable {
        private MyMiddleware mw;
        /**
            Constructor.
            @param mw: MyMiddleware object to get data from.
        */
        public LoggerRunnable(MyMiddleware mw) {
            this.mw = mw;
        }

        /**
            Override called when launching the thread.
        */
        @Override
        public void run() {
            try {
                ANA_LOG.info(Worker.getRecord(mw.workers, mw.queue.size()));
            } catch(InterruptedException ex) {
                SYS_LOG.info("Scheduled logger was interrupted while printing to logfile.");
            }
        }
    }

    /**
        Class Shutdown extending Thread. This can be used as a shutdown hook.
    */
    private class ShutDown extends Thread {
        private MyMiddleware mw;
        /**
            Constructor.
            @param mw: MyMiddleware object to get data from before shutting down.
        */
        public ShutDown(MyMiddleware mw) {
            this.mw = mw;
        }

        /**
            Override called when the thread is launched. This should only run on shutdown.
        */
        @Override
        public void run() {
            mw.timeRun += System.nanoTime() >> 10;
            SYS_LOG.info("Shutting down middleware cleanly after OS signal reception.");
            threadPool.shutdownNow();
            try {
                threadPool.awaitTermination(10, TimeUnit.SECONDS);
                serverChannel.close();
            } catch(InterruptedException ex) {
                SYS_LOG.info("Some threads might not have finished shutting down properly.");
            } catch(IOException ex) {
                SYS_LOG.info("The ServerSocketChannel did not close properly");
            }
            MyMiddleware.ses.shutdown();

            // Print to file and console, note loggers do not work in shutdown hooks
            try {
                PrintWriter out = new PrintWriter(new FileWriter(mw.home + "/analysis.log", true));
                out.println(Worker.getFinalStats(mw.workers, mw.timeRun));
                out.flush();
            } catch(IOException ex) {
                System.out.println("ATTENTION: Could not print final statistics to log file.");
            } finally {
                System.out.println(Worker.getFinalStats(mw.workers, mw.timeRun));
            }
        }
    }
}
