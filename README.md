# Middleware
Middleware serving as an intermediary between virtual clients and memcached servers. Responsible for serving requests, load balancing among memcached servers and potentially sharding read requests.

## TODO
1. Set up JAVA_HOME, ANT_HOME and PATH correctly on middleware machine (others do not really require ant and Java).
2. Perform benchmarking tests to see saturation limits of servers and clients.
3. Finish middleware and deploy

## Design
### Main structure
A single `BlockingQueue` serving multiple threads handling server connections and load balancing. The exact number of threads is determined at runtime by system arguments. Note that each worker thread is connected to all memcached servers at all times.


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
