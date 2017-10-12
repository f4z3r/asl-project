# Middleware
## TODO
1. Set up JAVA_HOME, ANT_HOME and PATH correctly on middleware machine (others do not really require ant and Java).
2. Perform benchmarking tests to see saturation limits of servers and clients.
3. Finish middleware and deploy

## Design
##### Main Thread
The main thread accepts connections from clients and creates `Request` objects to add to a `BlockingQueue` to be processed by a pool of worker threads. The responsibility of the main thread is only the instantiation of the server socket to listen to clients and the accepting of connections. Moreover, it will spawn a timed task to print out analysis (non-critical) logging information. All system critical logging will be performed by a different logger that writes directly to file. On the other hand, the analysis logger will write to a write buffer which is periodically written to file. These periodical writes to disk are performed by the spawned timed task (ca. every 5 seconds) in order to reduce overhead created by logging to file. Note that all connections are kept open until all work is performed. Hence the listener socket should never close and the IO file headers should only be closed as the middleware shuts down.

##### Worker Threads
The worker threads are responsible for the request handling. Upon instantiation, they **each** should connect to **all** memcached servers in order to perform request sharding and distributed write instructions. Note that these connections should never be closed either. 


## Project file structure
```
/app
    /build          -- build of the middleware
    /dist           -- jar distribution files
    /src            -- Source code
        /logging    -- logging formatters
        /util       -- utility libraries
        MyMiddleware.java
        RunMW.java
    build.xml       -- ANT build file
    README.md       -- recap of commands to build run

/logs           -- contains logfiles copied from the cloud

/scripts        -- contains all scripts to automate tasks on the cloud
    /local      -- contains scripts that get imported by ssh commands
                   (do not contain connections commands)
```
