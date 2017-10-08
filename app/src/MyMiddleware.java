/*
MyMiddleware.java
04-10-2017

Jakob Beckmann
*/

package asl_project;

import java.util.List;
import java.util.logging.*;
import java.io.*;
import java.net.*;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import asl_project.logging.*;
import asl_project.util.*;

public class MyMiddleware {
    private String IP;
    private int PORT;
    private List<String> SERVER_ADDRESSES;
    private int THREAD_COUNT;
    private boolean SHARDED;

    // Requests queue
    private BlockingQueue<Request> queue;

    // Loggers
    private static final Logger SYS_LOG = Logger.getLogger("Reporting");
    private static final Logger ANA_LOG = Logger.getLogger("Analsys");

    public MyMiddleware(String myIp, int port, List<String> mcAddresses, int numThreadsPTP, boolean readSharded) {
        this.IP = myIp;
        this.PORT = port;
        this.SERVER_ADDRESSES = mcAddresses;
        this.THREAD_COUNT = numThreadsPTP;
        this.SHARDED = readSharded;
        this.queue = new LinkedBlockingQueue<Request>();

        // Set up configurations for loggers
        try {
            FileHandler fh = new FileHandler("~/report.log", true);
            SysFormatter formatter = new SysFormatter();
            fh.setFormatter(formatter);
            SYS_LOG.addHandler(fh);
            SYS_LOG.setUseParentHandlers(false);
        } catch(Exception ex) {
            ex.printStackTrace();
        }
        try {
            FileHandler fh = new FileHandler("~/analysis.log", true);
            AnaFormatter formatter = new AnaFormatter();
            fh.setFormatter(formatter);
            ANA_LOG.addHandler(fh);
            ANA_LOG.setUseParentHandlers(false);
        } catch(Exception ex) {
            ex.printStackTrace();
        }
        SYS_LOG.setLevel(Level.CONFIG);
        ANA_LOG.setLevel(Level.FINEST);
    }

    public void run() {
        // Declare server socket
        ServerSocket serverSocket = null;
        // Set up server socket to listen to clients
        try {
            serverSocket = new ServerSocket(this.PORT);
        } catch(IOException ex) {
            SYS_LOG.severe("Server socket could not be set up.");
            System.exit(1);
        }
        SYS_LOG.config(String.format("Server socket set up on port %d. Launching %d worker threads.", this.PORT, this.THREAD_COUNT));

        // Launch worker threads
        for(int idx = 0; idx < this.THREAD_COUNT; idx++) {
            new Thread(new WorkerThread(this.queue, idx, this.SERVER_ADDRESSES, this.SHARDED)).start();
        }
    }
}
