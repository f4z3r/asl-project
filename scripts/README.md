# /scripts
This directory contains all scripts used to automate testing on the cloud.

## `automator.bash`
Run this script by using `automator.bash run` to run all experiments. Note that in order to do this, one needs a directory `~/Desktop/logs` that will be used as a temporary directory for the currently running experiment by the script. In order to modify which experiments to run, comment out lines at the very end of the script file where the experiments that will be run are listed.

## `network_check.bash`
Checks network bandwidth between machines. To run this script use `network_check.bash run`.
