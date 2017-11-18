# Middleware

## TODO
1. Complete remaining experiments.
2. Find optimal configuration based on benchmarks.
3. Write report.

## Dir structure
Use the following dir structure for experiments:
```
/date(name)
    /n_workers
        /x_threads_y_clients_operation
            /clients
                /clientm_123.log
```
Reorder into the following structure when preprocessing data:
```
/name
    /operation
        /n_workers
            /m_clients
                /clientx
                    /rep123.csv
```
The number of threads on memtier is implicit here as it does not change between experiments.

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
    /final          -- final processed data used for analysis and graphing
    /preprocessed   -- data from logs (removed unnecessary )
    /processed      -- processed data, client cumulated, etc.
    procssing script ...
```

## Notes to myself
- Note that in the memcached benchmarking experiment, client host #2 is has much higher latency due to network latencies.
- Note that in mw2 experiment, we have data getting evicted over long read without write periods (2.5h), starts at rates lower than 1%, increases to ...
- Repeat baselines without middleware if enough resources at very end. Alternate reads and writes to reduce the amount of evicted data.
- Repeat baseline with 2 mws if enough resources and make sure the pings are acceptable.
