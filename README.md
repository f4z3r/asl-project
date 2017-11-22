# Middleware

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
    README.md

/scripts            -- contains all scripts to automate tasks on the cloud
/logs               -- contains all experiment raw logs
/processing
    /final          -- final processed data used for analysis and graphing
    /processed      -- processed data, client cumulated, etc.
    preprocess.py   -- preprocessed raw logs from /logs/ into cumulated data
                       in /processing/processed/
    aggregate.py    -- aggregates processed data from experiments
                       (/processing/processed/) into a single data.csv file in
                       /processing/final/
    aggregate_stat.py   -- aggregates processed dstat data from experiments
                           (/processing/processed/) into a single dstat.csv file in
                           /processing/final/
    handle_dstat.py -- preprocesses dstat data from dstat raw logs
    README.md

README.md           -- this file
report.tex          -- the tex file generating the report
project.pdf         -- project description as given by the course
report-outline.pdf  -- report outline as given by the course
azure_template.json -- JSON template used to generate VMs on the cloud
```

## Graphs
Note that unless explicitly stated otherwise in the report, every graph is generated from the data contained in the data.csv and dstat.csv files of the respective experiment. These files can be found the under `/processing/final/<experiment_name>/`. In order to check exactly which data point is graphed to what, the individual graphs are stored in the Excel workbooks that can be found in the same directory. One can check exactly what subsection of the data contained in data.csv is used for a specific graph.

## Notes on standard deviations and means (stated in report)
The standard deviations in the `/processing/processed/**` subfiles is computed the following way:
- For a single subclient/middleware, the standard deviation is taken as the deviation of throughtputs/latencies logged every second by the client/middleware machines.
- For an aggregate of subclients/clients/middlewares, the standard deviation is taken as the deviation of the averages of subclients/clients/middlewares computed every second during the experiment.

The averages are taken as averages of the total available data. Note that internally (within the scripts), this is computed as an average of averages. However, as the number of measurements is exactly 80 across all processed logs, this is equivalent to an overall average.

Consider the following:
- Take the overall average (n1 + n2 + n3 + ...) / (80 * num_clients * ...)
- Take average of averages (n1/80 + n2/80 + n3/80 + ...) / (num_clients * ...)

In the second case, the division can be factored out and we obtain the same as in the first case.

Note however, that in the final data, standard deviations of the averages across repetitions are also included (i.e. how individual repetitions deviate from each other).
