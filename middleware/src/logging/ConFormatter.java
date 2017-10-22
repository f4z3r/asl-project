/*
    ConFormatter.java
    17-10-2017

    @Description:Formatter for performance analysis. Prints the record message without any additional information.

    @Author: Jakob Beckmann
*/

package asl_project.logging;

import java.util.logging.*;


public class ConFormatter extends Formatter {
    public String format(LogRecord record) {
        StringBuilder builder = new StringBuilder(1000);
        builder.append(formatMessage(record)).append("\n");
        return builder.toString();
    }

    public String getHead(Handler handler) {
        return super.getHead(handler);
    }

    public String getTail(Handler handler) {
        return super.getTail(handler);
    }
}
