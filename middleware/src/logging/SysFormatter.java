/*
    SysFormatter.java
    17-10-2017

    @Description: Formatter for system error reporting. Prints errors using the following structure:
        dd/MM/yy HH:mm:ss:SSS - [function.trace] - [LEVEL] - message

    @Author: Jakob Beckmann
*/

package asl_project.logging;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.*;


public class SysFormatter extends Formatter {
    private static final DateFormat df = new SimpleDateFormat("dd/MM/yy HH:mm:ss:SSS");

    public String format(LogRecord record) {
        StringBuilder builder = new StringBuilder(1000);
        builder.append(df.format(new Date(record.getMillis()))).append(" - ");
        builder.append("[").append(record.getSourceClassName()).append(".");
        builder.append(record.getSourceMethodName()).append("] - ");
        builder.append("[").append(record.getLevel()).append("] - ");
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
