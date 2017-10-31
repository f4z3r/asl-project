/**
    Worker.java
    21-10-2017

    @Description: Implements a worker thread that will take requests from the queue filled by the middleware and process these requests. On initialisation, it will connnect to all Memcached servers and keep the connections alive until the middleware is shutdown.
    @Author: Jakob Beckmann
*/

package asl_project.util;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.CountDownLatch;
import java.nio.channels.*;
import java.nio.ByteBuffer;
import java.net.InetSocketAddress;
import java.io.IOException;
import java.util.logging.Logger;


/**
    Worker class implementing Runnable to be launched as a thread within the TheadPool in MyMiddleware.
*/
public class Worker implements Runnable {
    // This is a flag to clear the histogram on the first call to getRecord()
    private static boolean clear_histogram = true;

    // Static fields for analysis
    private int hist_count = 0;
    private int count_set = 0;
    private int count_get = 0;
    private int count_multiget = 0;
    private int count_invalid = 0;
    private int count_set_interval = 0;
    private int count_get_interval = 0;
    private int count_multiget_interval = 0;
    private int count_invalid_interval = 0;
    private int hits_set = 0;
    private int hits_get = 0;
    private int hits_multiget = 0;
    private int hits_interval = 0;
    private long total_time_set = 0L;
    private long total_time_get = 0L;
    private long total_time_multiget = 0L;
    private long total_time_invalid = 0L;
    private long total_time_interval = 0L;
    private long total_proc_time_set = 0L;
    private long total_proc_time_get = 0L;
    private long total_proc_time_multiget = 0L;
    private long total_proc_time_invalid = 0L;
    private long total_q_time = 0L;
    private long total_q_time_interval = 0L;
    private long total_server_time_set = 0L;
    private long total_server_time_get = 0L;
    private long total_server_time_multiget = 0L;
    private long total_server_time_invalid = 0L;
    private long total_server_time_interval = 0L;

    // Histogram
    public ArrayList<Integer> histogram;


    // Logger
    private static final Logger SYS_LOG = Logger.getLogger("System");

    // Private fields
    private BlockingQueue<Request> queue;
    private int id;
    private boolean sharded;
    private ArrayList<SocketChannel> connections;
    private int serverCount;

    // Used to block the complete function when logging is performed.
    private CountDownLatch lock_complete;
    private CountDownLatch lock_logger;

    // Variable used for load balancing
    private static int server = 0;



    /**
        Contructor. Creates a runnable object listening for requests on queue and processing them with the servers listen in its third argument, potentially sharding reads.
        @param queue: A blocking queue of requests. This is the queue the worker thread will get the requests to process from.
        @param threadID: Integer giving the unique ID for the middleware to be able to identify it.
        @param mcAddresses: List of strings containing all addresses and ports of the Memcached servers the worker will connect to.
        @param readSharded: Boolean for read sharding. See MyMiddleware for more information.
    */
    public Worker(BlockingQueue<Request> queue, int threadID, List<String> mcAddresses, boolean readSharded) {
        this.queue = queue;
        this.id = threadID;
        this.sharded = readSharded;
        this.connections = new ArrayList<SocketChannel>();
        this.lock_complete = new CountDownLatch(0);
        this.lock_logger = new CountDownLatch(0);
        this.histogram = new ArrayList<Integer>();

        // Generate sockets for the Memcached servers
        for(String address: mcAddresses) {
            String host = address.split(":")[0];
            int port = Integer.parseInt(address.split(":")[1]);
            SocketChannel connection;
            try {
                connection = SocketChannel.open(new InetSocketAddress(host, port));
                connection.configureBlocking(true);
                connections.add(connection);
            } catch(IOException ex) {
                SYS_LOG.warning("A connection with a Memcached server could not be established for thread " + this.id);
            }
        }

        this.serverCount = connections.size();
    }


    /**
        Override of the run() function from Runnable. This runs the worker thread when the thread is started.
    */
    @Override
    public void run() {
        byte[] barray = new byte[4096];
        while(true) {
            // First check if the thread has been interrupted
            if(Thread.interrupted()) {
                for(SocketChannel connection: connections) {
                    try {
                        connection.close();
                    } catch(IOException ex) {
                        SYS_LOG.info("A connection to a Memcached server could not be closed on shutdown for thread " + this.id);
                    }
                }
                return;
            }

            // Process requests since the thread is not interrupted
            try {
                Request request = queue.take();            // This blocks until a request becomes available
                request.time_dqed = System.nanoTime() >> 10;            // In microseconds


                // Parse request to find out type
                if(!request.parse()) {
                    // The command sent by the client is invalid, send ERROR back
                    request.channel.write(ByteBuffer.wrap("ERROR\r\n".getBytes()));
                    completed(request);
                    continue;
                }


                ByteBuffer response = ByteBuffer.allocate(4096);
                if(this.sharded && request.type == Request.Type.MULTIGET) {
                    // ===================================================================================================
                    // SHARDED MUTLIGET
                    // ===================================================================================================
                    response = shardedRead(request);
                } else if(request.type == Request.Type.SET) {
                    // ===================================================================================================
                    // SET REQUEST: send request to all servers
                    // ===================================================================================================
                    request.time_mmcd_sent = System.nanoTime() >> 10;       // In microseconds
                    for(int server = 0; server < this.serverCount; server++) {
                        connections.get(server).write(request.buffer);
                    }

                    String response_str = "";
                    request.hit = true;
                    for(int server = 0; server < this.serverCount; server++) {
                        ByteBuffer responseSvr = ByteBuffer.allocate(128);
                        byte[] responseByte = new byte[128];
                        connections.get(server).read(responseSvr);
                        responseSvr.flip();
                        responseSvr.get(responseByte, 0, responseSvr.limit());
                        response_str = new String(Arrays.copyOfRange(responseByte, 0, responseSvr.limit()));
                        // Check if the server reponded something else than stored
                        if(!response_str.equals("STORED\r\n")) {
                            System.out.println("Entered notstored if");
                            request.time_mmcd_rcvd = System.nanoTime() >> 10;       // In microseconds
                            request.hit = false;
                            // It did, relay the message to the client
                            request.channel.write(ByteBuffer.wrap(response_str.getBytes()));
                            System.out.println("notstored sent to client");
                            completed(request);
                            break;
                        }
                    }
                    request.time_mmcd_rcvd = System.nanoTime() >> 10;       // In microseconds
                    if(request.hit == false) {
                        // Request is completed, skip to next request
                        continue;
                    }
                    // All servers desponded with STORED
                    request.channel.write(ByteBuffer.wrap(response_str.getBytes()));
                    completed(request);
                    // Request is completed, skip to next request
                    continue;
                } else {
                    // ===================================================================================================
                    // GET / NON-SHARDED MULTIGET
                    // ===================================================================================================
                    // Load balancing
                    int server = Worker.getServer() % this.serverCount;

                    // Send request to server
                    request.time_mmcd_sent = System.nanoTime() >> 10;       // In microseconds
                    connections.get(server).write(request.buffer);

                    // Get response from server
                    connections.get(server).read(response);
                    request.time_mmcd_rcvd = System.nanoTime() >> 10;       // In microseconds
                    response.flip();
                }

                // Check for hits or misses.
                response.get(barray, 0, response.limit());
                String response_str = new String(Arrays.copyOfRange(barray, 0, response.limit())).trim();
                if(!response_str.equals("END") && !response_str.equals("ERROR") && !response_str.equals("SERVER_ERROR") && !response_str.equals("CLIENT_ERROR") && !response_str.equals("NOT_STORED")) {
                    request.hit = true;
                }
                response.rewind();


                request.channel.write(response);

                completed(request);

            } catch(IOException ex) {
                SYS_LOG.info("Error communicating with client or server.");
            } catch(InterruptedException ex) {
                SYS_LOG.info(String.format("Thread %d was interrupted. Shutting it down.", this.id));
                Thread.currentThread().interrupt();
            }
        }
    }

    /**
        This function is used for load balancing. It basically just increments a counter and the server takes this modulo the number of servers to get the server it should access.
        @return Integer
    */
    private static synchronized int getServer() {
        return Worker.server++;
    }


    /**
        This function takes care of sharding multigets across servers and return their composite response.
        @param request: Request to be sharded
        @return ByteBuffer that contains the aggregated responses of the servers.
    */
    private ByteBuffer shardedRead(Request request) throws IOException {
        ByteBuffer response = ByteBuffer.allocate(4096);

        // Get the individual keys in the get command
        byte[] commandArray = new byte[4096];
        request.buffer.get(commandArray, 0, request.buffer.limit() - 2);
        String command = new String(Arrays.copyOfRange(commandArray, 0, request.buffer.limit() - 2)).trim();
        String[] arguments = command.split(" ");

        if(arguments.length - 1 < this.serverCount) {
            // We have less arguments than available servers

            // Use to keep track which servers were used
            int[] servers = new int[this.serverCount];
            request.time_mmcd_sent = System.nanoTime() >> 10;       // In microseconds
            for(int idx = 1; idx < arguments.length; idx++) {
                int server = Worker.getServer() % this.serverCount;
                // Keep track of which servers we sent a request to
                servers[server] = 1;
                connections.get(server).write(ByteBuffer.wrap(("get " + arguments[idx] + "\r\n").getBytes()));
            }
            for(int idx = 0; idx < servers.length; idx++) {
                if(servers[idx] == 1) {
                    // We sent a request to that server hence read response
                    this.connections.get(idx).read(response);
                    response.flip();
                    // Remove the "END\r\n" of the end of the message
                    response.position(response.limit() - 5);
                }
                request.time_mmcd_rcvd = System.nanoTime() >> 10;       // In microseconds
            }
        } else {
            // We have more arguments than available servers
            request.time_mmcd_sent = System.nanoTime() >> 10;       // In microseconds
            for(int server = 0; server < this.serverCount; server++) {
                String commandSvr = "get";
                for(int idx = server + 1; idx < arguments.length; idx += this.serverCount) {
                    commandSvr += " " + arguments[idx];
                }
                commandSvr += "\r\n";
                connections.get(server).write(ByteBuffer.wrap(commandSvr.getBytes()));
            }
            for(int server = 0; server < this.serverCount; server++) {
                this.connections.get(server).read(response);
                response.flip();
                // Remove the "END\r\n" of the end of the message
                response.position(response.limit() - 5);
            }
            request.time_mmcd_rcvd = System.nanoTime() >> 10;       // In microseconds
        }
        response.rewind();
        if(response.limit() > 7) {
            request.hit = true;
        }
        return response;
    }

    // ======================================================================================
    // STATISTICS
    // ======================================================================================
    /**
        Gathers information about the request. Note that this blocks the logger from accessing this workers statistics.
        @param request: Request object from which to gather data.
    */
    private synchronized void completed(Request request) throws InterruptedException {
        request.time_completed = System.nanoTime() >> 10;   // In microseconds
        this.hist_count++;

        if(request.type == Request.Type.SET) {
            this.count_set++;
            this.count_set_interval++;
            this.total_time_set += (request.time_completed - request.time_created);
            this.total_proc_time_set += (request.time_completed - request.time_dqed);
            this.total_server_time_set += (request.time_mmcd_rcvd - request.time_mmcd_sent);
            if(request.hit == true) {
                this.hits_set++;
                this.hits_interval++;
            }
        } else if(request.type == Request.Type.GET) {
            this.count_get++;
            this.count_get_interval++;
            this.total_time_get += (request.time_completed - request.time_created);
            this.total_proc_time_get += (request.time_completed - request.time_dqed);
            this.total_server_time_get += (request.time_mmcd_rcvd - request.time_mmcd_sent);
            if(request.hit == true) {
                this.hits_get++;
                this.hits_interval++;
            }
        } else if(request.type == Request.Type.MULTIGET) {
            this.count_multiget++;
            this.count_multiget_interval++;
            this.total_time_multiget += (request.time_completed - request.time_created);
            this.total_proc_time_multiget += (request.time_completed - request.time_dqed);
            this.total_server_time_multiget += (request.time_mmcd_rcvd - request.time_mmcd_sent);
            if(request.hit == true) {
                this.hits_multiget++;
                this.hits_interval++;
            }
        } else {
            this.count_invalid++;
            this.count_invalid_interval++;
            this.total_time_invalid += (request.time_completed - request.time_created);
            this.total_proc_time_invalid += (request.time_completed - request.time_dqed);
            this.total_server_time_invalid += (request.time_mmcd_rcvd - request.time_mmcd_sent);
        }

        this.total_time_interval += (request.time_completed - request.time_created);
        this.total_proc_time_interval += (request.time_completed - request.time_dqed);
        this.total_q_time += (request.time_dqed - request.time_created);
        this.total_q_time_interval += (request.time_dqed - request.time_created);
        this.total_server_time_interval += (request.time_mmcd_rcvd - request.time_mmcd_sent);

        // Add one to the corresponding index of the histogram
        // Note that we add one to the element at index equal to the response time (in 0.1 ms) interval - 1
        // Hence for a response time of 2.3343 milliseconds, we add one to the element at index 23
        int index = (int) (request.time_completed - request.time_created) / 100;
        if(index >= this.histogram.size()) {
            for(int i = this.histogram.size(); i <= index; i++) {
                this.histogram.add(0);
            }
        }
        this.histogram.set(index, this.histogram.get(index) + 1);
    }

    /**
        This function should be used when initialising the analysis log file.
        @return String containing the column titles of the statistical output of the middleware.
    */
    public static String initLog() {
        return String.format("%6s %6s %9s %5s %6s %9s %9s %9s %5s",
                             "SETS",
                             "GETS",
                             "MULTIGETS",
                             "IVLD",
                             "HITS",
                             "RSP TIME",
                             "Q TIME",
                             "SVR TIME",
                             "Q LEN");
    }


    /**
        This function aggregates statistical data from all workers given as arguments. Note that this function blocks workers from completing tasks while data is read from them.
        @param workers: ArrayList of Worker from which to retrieve data.
        @param queueLength: Integer of the queue length to be written in the last column.
        @return String containing data aggregated since the last call to this function.
    */
    public static String getRecord(ArrayList<Worker> workers, int queueLength) throws InterruptedException {
        int result_count_set_interval = 0;
        int result_count_get_interval = 0;
        int result_count_multiget_interval = 0;
        int result_count_invalid_interval = 0;
        int result_hits_interval = 0;
        long result_total_time = 0L;
        long result_total_q_time = 0L;
        long result_total_server_time = 0L;


        for(Worker worker: workers) {
            // Block the worker from writing to its statistic values
            synchronized(worker) {
                result_count_set_interval += worker.count_set_interval;
                result_count_get_interval += worker.count_get_interval;
                result_count_multiget_interval += worker.count_multiget_interval;
                result_count_invalid_interval += worker.count_invalid_interval;
                result_hits_interval += worker.hits_interval;
                result_total_time += worker.total_time_interval;
                result_total_q_time += worker.total_q_time_interval;
                result_total_server_time += worker.total_server_time_interval;

                // Reset values for each worker
                worker.count_set_interval = 0;
                worker.count_get_interval = 0;
                worker.count_multiget_interval = 0;
                worker.count_invalid_interval = 0;
                worker.hits_interval = 0;
                worker.total_time_interval = 0L;
                worker.total_q_time_interval = 0L;
                worker.total_server_time_interval = 0L;

                // If the clear_histogram is true, clear the histograms of the workers
                // and reset all statistics.
                if(Worker.clear_histogram) {
                    worker.histogram = new ArrayList<Integer>();
                    worker.hist_count = 0;
                }
            }
        }

        // Set the clear_histogram to be false, it hence get triggered only on the first call to this function
        Worker.clear_histogram = false;

        int result_count_interval = result_count_get_interval + result_count_set_interval + result_count_multiget_interval + result_count_invalid_interval;
        double result_response_time = result_total_time / (double) result_count_interval;
        double result_q_time = result_total_q_time / (double) result_count_interval;
        double result_server_time = result_total_server_time / (double) result_count_interval;

        String result = String.format("%6d %6d %9d %5d %6d %9.2f %9.2f %9.2f %5d",
                                      result_count_set_interval,
                                      result_count_get_interval,
                                      result_count_multiget_interval,
                                      result_count_invalid_interval,
                                      result_hits_interval,
                                      result_response_time,
                                      result_q_time,
                                      result_server_time,
                                      queueLength);

        return result;
    }

    /**
        Prints final statistics. This function should be called as the middleware shuts down. Note that this function does not need a lock as all worker threads will have shutdown by the time it is called. And getRecord does not write to the data this function tries to access.
        @param workers: ArrayList of Worker from which to retrieve data.
        @param timeRun: Long containing the runtime of the middleware in microseconds.
        @return String containing the final statistics and histogram
    */
    public static String getFinalStats(ArrayList<Worker> workers, long timeRun) {
        long timeRunSec = timeRun >> 20;            // Convert from microseconds to seconds

        String result = new String(new char[60]).replace('\0', '=') + "\nALL STATS (timing measures are in microseconds)\n";
        result = result.concat(String.format("%-9s|%-9s|%-9s|%-9s|%-9s|%-9s|%-9s|%-9s\n", "Type", "Total", "Ops/sec", "Hits/sec", "Miss/Sec", "Resp Time", "Proc Time", "Srvr Time"));

        int maxHistogramSize = 0;
        ArrayList<Integer> histogram = new ArrayList<Integer>();

        int hist_count_total = 0;

        int type_set = 0;
        int type_get = 0;
        int type_multiget = 0;
        int type_invalid = 0;

        int type_hit_set = 0;
        int type_hit_get = 0;
        int type_hit_multiget = 0;

        long resp_time_set = 0L;
        long resp_time_get = 0L;
        long resp_time_multiget = 0L;
        long resp_time_invalid = 0L;

        long proc_time_set = 0L;
        long proc_time_get = 0L;
        long proc_time_multiget = 0L;
        long proc_time_invalid = 0L;

        long srvr_time_set = 0L;
        long srvr_time_get = 0L;
        long srvr_time_multiget = 0L;
        long srvr_time_invalid = 0L;

        for(Worker worker: workers) {
            type_set += worker.count_set;
            type_get += worker.count_get;
            type_multiget += worker.count_multiget;
            type_invalid += worker.count_invalid;

            type_hit_set += worker.hits_set;
            type_hit_get += worker.hits_get;
            type_hit_multiget += worker.hits_multiget;

            resp_time_set += worker.total_time_set;
            resp_time_get += worker.total_time_get;
            resp_time_multiget += worker.total_time_multiget;
            resp_time_invalid += worker.total_time_invalid;

            proc_time_set += worker.total_proc_time_set;
            proc_time_get += worker.total_proc_time_get;
            proc_time_multiget += worker.total_proc_time_multiget;
            proc_time_invalid += worker.total_proc_time_invalid;

            srvr_time_set += worker.total_server_time_set;
            srvr_time_get += worker.total_server_time_get;
            srvr_time_multiget += worker.total_server_time_multiget;
            srvr_time_invalid += worker.total_server_time_invalid;

            hist_count_total += worker.hist_count;


            // Create a cummulative histogram from data from workers
            if(worker.histogram.size() > maxHistogramSize) {
                for(int idx = maxHistogramSize; idx < worker.histogram.size(); idx++) {
                    histogram.add(0);
                }
                maxHistogramSize = worker.histogram.size();
            }

            for(int idx = 0; idx < worker.histogram.size(); idx++) {
                histogram.set(idx, histogram.get(idx) + worker.histogram.get(idx));
            }
        }

        result = result.concat(String.format("%-9s|%9d|%9.2f|%9.2f|%9.2f|%9.2f|%9.2f|%9.2f\n",
                                             "SET",
                                             type_set,
                                             type_set / (double) timeRunSec,
                                             type_hit_set / (double) timeRunSec,
                                             (type_set - type_hit_set) / (double) timeRunSec,
                                             resp_time_set / (double) type_set,
                                             proc_time_set / (double) type_set,
                                             srvr_time_set / (double) type_set));

        result = result.concat(String.format("%-9s|%9d|%9.2f|%9.2f|%9.2f|%9.2f|%9.2f|%9.2f\n",
                                             "GET",
                                             type_get,
                                             type_get / (double) timeRunSec,
                                             type_hit_get / (double) timeRunSec,
                                             (type_get - type_hit_get) / (double) timeRunSec,
                                             resp_time_get / (double) type_get,
                                             proc_time_get / (double) type_get,
                                             srvr_time_get / (double) type_get));

        result = result.concat(String.format("%-9s|%9d|%9.2f|%9.2f|%9.2f|%9.2f|%9.2f|%9.2f\n",
                                             "MULTIGET",
                                             type_multiget,
                                             type_multiget / (double) timeRunSec,
                                             type_hit_multiget / (double) timeRunSec,
                                             (type_multiget - type_hit_multiget) / (double) timeRunSec,
                                             resp_time_multiget / (double) type_multiget,
                                             proc_time_multiget / (double) type_multiget,
                                             srvr_time_multiget / (double) type_multiget));

        result = result.concat(String.format("%-9s|%9d|%9.2f|%9s|%9s|%9.2f|%9.2f|%9s\n",
                                             "INVALID",
                                             type_invalid,
                                             type_invalid / (double) timeRunSec,
                                             "---",
                                             "---",
                                             resp_time_invalid / (double) type_invalid,
                                             proc_time_invalid / (double) type_invalid,
                                             "---"));

        result = result.concat("\n\n HISTOGRAM\n");
        result = result.concat(String.format("%20s%10s\n", "Response time (ms)", "Percent"));

        // Running sum used for percentiles
        int runningSum = 0;
        for(int idx = 0; idx < histogram.size(); idx++) {
            runningSum += histogram.get(idx);
            result = result.concat(String.format("%20.1f%10.2f%%\n", (idx + 1) / 10.0f, 100 * runningSum / (double) hist_count_total));
        }

        return result;
    }
}
