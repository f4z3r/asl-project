/*
Request.java
04-10-2017

Class that stores a socket and the time it got submitted to queue.

Jakob Beckmann
*/

package asl_project.util;

import java.net.*;
import java.time.LocalDateTime;
import java.io.*;

public class Request {
    private Socket socket;
    private LocalDateTime timeRequested;
    public DataInputStream in;
    public DataOutputStream out;

    public Request(Socket socket) {
        this.timeRequested = LocalDateTime.now();
        this.socket = socket;
    }

    public Socket getSocket() {
        return this.socket;
    }

    public void generateStreams() throws IOException {
        this.in = new DataInputStream(this.socket.getInputStream());
        this.out = new DataOutputStream(this.socket.getOutputStream());
    }
}
