/*
WorkerThread.java
04-10-2017

Thread performing the request processing. Note that each thread just handles a single request sequentially.

Jakob Beckmann
*/

package asl_project.util;

import java.util.concurrent.BlockingQueue;
import java.util.ArrayList;
import java.util.List;
import java.io.IOException;
import java.util.logging.*;

public class WorkerThread implements Runnable {
    private BlockingQueue<Request> queue;
    private int ID;
    private boolean SHARDED;
    private ArrayList<MemcachedConnection> CONNECTIONS;

    private static final Logger SYS_LOG = Logger.getLogger("Reporting");
    private static final Logger ANA_LOG = Logger.getLogger("Analsys");

    public WorkerThread(BlockingQueue<Request> queue, int threadID, List<String> mcAddresses, boolean readSharded) {
        this.queue = queue;
        this.ID = threadID;
        this.SHARDED = readSharded;
        this.CONNECTIONS = new ArrayList<MemcachedConnection>();

        // Generate sockets for memacached server connections
        for(String address: mcAddresses) {
            String host = address.split(":")[0];
            int port = Integer.parseInt(address.split(":")[1]);
            try(MemcachedConnection connection = new MemcachedConnection(host, port);) {
                this.CONNECTIONS.add(connection);
            } catch(IOException ex) {
                SYS_LOG.warning(String.format("Connection to server %s:%d could not be established.", host, port));
            }
        }
        SYS_LOG.info(String.format("Finished instantiating thread %d", this.ID));
    }

    public void run() {
        SYS_LOG.info(String.format("Thread %d started running.", this.ID));
        ANA_LOG.info("some numbers");

        // TODO implement

    }

    private ArrayList<Request> parseRequest(Request request) {

        // TODO implement request sharding

        return null;
    }

    private MemcachedConnection getServer() {

        // TODO implement load balancing

        return null;
    }
}
