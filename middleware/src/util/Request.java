/**
    Request.java
    21-10-2017

    @Description: Implements a request from a client. This will contain a buffer for the message as well as collect timestamps for analysis of the request. Each request will be linked to one SelectionKey for each event triggered by the selector. Hnece this class is also responsible for handling incomplete requests.
    @Author: Jakob Beckmann
*/

package asl_project.util;

import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.logging.*;
import java.util.Arrays;
import java.util.ArrayList;

/**
    TODO
*/
public class Request {
    // Logger
    private static final Logger SYS_LOG = Logger.getLogger("System");

    // Type enum
    public static enum Type {
        MULTIGET,
        GET,
        SET,
        INVALID,
    }

    // Non-static fields
    public SelectionKey key;
    public ByteBuffer buffer;
    public SocketChannel channel;
    public int messageLength;
    private int commandLength;
    private int dataLength;
    public Type type;
    public boolean hit;
    public int multigetLength;

    // Timing fields
    public long time_created;
    public long time_dqed;
    public long time_mmcd_sent;
    public long time_mmcd_rcvd;
    public long time_completed;


    /**
        Constructor. Builds a request object. Note that this creates a timestamp for the time of creating that can be later used in statistics.
        @param buffer: ByteBuffer containing the message of sent by the client.
        @param key: SelectionKey associated with the OP_READ event that triggered the creation of this request.
    */
    public Request(ByteBuffer buffer, SelectionKey key){
        this.time_created = System.nanoTime() >> 10;        // In microseconds

        this.key = key;
        this.buffer = buffer;
        this.channel = (SocketChannel) key.channel();
        this.hit = false;
        this.type = Type.INVALID;
    }

    /**
        Parses the request to ckeck its type and if it is complete.
        @return true if the command could be parsed and is complete.
    */
    public boolean parse() {
        buffer.flip();
        messageLength = buffer.limit();
        // Check if the message finishes with "\r\n"
        if(buffer.get(messageLength - 1) != '\n' || buffer.get(messageLength - 2) != '\r') {
            SYS_LOG.warning("Incomplete request.");
            this.type = Type.INVALID;
            return false;
        }

        // Try to read the command
        buffer.rewind();
        char prev = (char) buffer.get();
        char curr = (char) buffer.get();
        while((prev != '\r' || curr != '\n') && buffer.hasRemaining()) {
            prev = curr;
            curr = (char) buffer.get();
        }
        commandLength = buffer.position();
        // Copy the command to a string
        byte[] barray = new byte[4096];
        buffer.rewind();        // Not flip as we dont want to set the limit to the end of the command
        buffer.get(barray, 0, commandLength - 2);
        String command = new String(Arrays.copyOfRange(barray, 0, commandLength)).trim();
        if(command.startsWith("get")) {
            int numGets = command.split(" ").length - 1;
            if(numGets > 1) {
                this.type = Type.MULTIGET;
                this.multigetLength = numGets;
            } else {
                this.type = Type.GET;
            }
        } else if(command.startsWith("set")) {
            this.type = Type.SET;
        } else {
            this.type = Type.INVALID;
        }

        // If the command is of type SET, check if all required data is in the message
        if(type == Type.SET) {
            try {
                dataLength = Integer.parseInt(command.trim().split(" ")[4]);
            } catch(ArrayIndexOutOfBoundsException ex) {
                // The command is not used correctly
                SYS_LOG.info("Client sent invalid command");
                this.type = Type.INVALID;
                return false;
            }

            if(messageLength != commandLength + dataLength + 2) {
                SYS_LOG.info("Incomplete request. Data is incomplete.");
                this.type = Type.INVALID;
                return false;
            }
        }
        buffer.rewind();
        return true;
    }
}
