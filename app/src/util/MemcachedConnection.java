/*
MemcachedConnection.java
04-10-2017

Class extending Socket that also stored input and output streams of its socket.

Jakob Beckmann
*/

package asl_project.util;

import java.net.*;
import java.io.*;

public class MemcachedConnection extends Socket {
    public DataInputStream in;
    public DataOutputStream out;

    public MemcachedConnection(String host, int port) throws IOException {
        super(host, port);
        this.in = new DataInputStream(this.getInputStream());
        this.out = new DataOutputStream(this.getOutputStream());
    }
}
