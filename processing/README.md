# /processing
This directory contains all non-raw log data and the scripts used to generate said data.

## Structure
```
/final                  -- final data used for the report
/processed              -- processed data from raw logs
/graphics               -- graphs used for the generation of the report

aggregate_dstat.py      -- script used to generate final dstat data
aggregate.py            -- script used to generate final data
handle_dstat.py         -- script used to generate prcessed dstat data
preprocess.py           -- script used to generate processed data
```

## Running script
In order to run the scripts in this directory use:
```
python3 <script> all
```
This will generate all processed/final data. However, note that to generate the final data, processed data must be provided in the correct format. Moreover, this will give you errors if the directories of the data you are trying to produce already exists. Hence to run the scripts please delete the `final` or `processed` directories and then run the scripts.
