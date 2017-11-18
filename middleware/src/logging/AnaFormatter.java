/*
    AnaFormatter.java
    17-10-2017

    @Description:Formatter for performance analysis. Prints errors using the following structure:
        dd/MM/yy HH:mm:ss:SSS - message

    @Author: Jakob Beckmann
*/

package asl_project.logging;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.*;


public class AnaFormatter extends Formatter {
    private static final DateFormat df = new SimpleDateFormat("dd/MM/yy HH:mm:ss:SSS");

    public String format(LogRecord record) {
        StringBuilder builder = new StringBuilder(1000);
        builder.append(df.format(new Date(record.getMillis()))).append(" - ");
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
