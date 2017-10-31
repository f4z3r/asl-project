# Middleware

## TODO
1. Install `dstat` and `screen` on all machines.
2. Complete the scripting code for the experiments and the automation of deployment.
3. Complete benchmarking experiments.
4. Complete remaining experiments.
5. Write report.


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
```
