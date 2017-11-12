# Middleware

## TODO
1. Complete remaining experiments.
2. Implement ping at beginning of each experiment ?
3. Write report.


## Project file structure
```
/middleware
    /build          -- build of the middleware
    /dist           -- jar distribution files
    /src            -- Source code
        /logging    -- logging formatters
        /util       -- utility libraries such as request and worker classes
        MyMiddleware.java
        RunMW.java
    build.xml       -- ANT build file
    README.md       -- recap of commands to build run

/scripts            -- contains all scripts to automate tasks on the cloud
/logs               -- contains all experiment raw logs
/processing
    /assets         -- final processed data used for analysis and graphing
    /preprocessed   -- data from logs (removed unnecessary )
    procssing script ...
```

## Notes to myself
- Note that in the memcached benchmarking experiment, client host #2 is has much higher latency due to network latencies.
