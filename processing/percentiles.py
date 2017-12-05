#!/usr/bin/env python3


import sys
import os
import csv
import re
import pandas as pd
import numpy as np

def percentiles():
    """Gathers client percentile information."""

    # Config
    name = "get_and_multigets"
    operation_list = ["0:9", "0:6", "0:3", "0:1"]
    sharded_list = ["true", "false"]
    worker_list = [64]
    client_list = [2]

    potential_dirs = os.listdir("/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/" +\
                                "autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs")
    exp_dir = [directory for directory in potential_dirs if not directory.find(name)]
    if len(exp_dir) != 1:
        print("Please make sure there is one and only one directory containing " +\
              "the experiment name")
        sys.exit(1)

    exp_dir = os.path.join("/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/" +\
                           "autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs",
                           exp_dir[0])

    output_dir = "final/get_and_multigets"
    outputfilename = os.path.join(output_dir, "percentile_info.csv")

    with open(outputfilename, 'w', newline="") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow([name.upper()])
        writer.writerow(["Percentile info"])
        writer.writerow([])
        writer.writerow(["Operation",
                         "Sharded",
                         "Average 25 percentile",
                         "Std 25 percentile",
                         "Average 50 percentile",
                         "Std 50 percentile",
                         "Average 75 percentile",
                         "Std 75 percentile",
                         "Average 90 percentile",
                         "Std 90 percentile",
                         "Average 99 percentile",
                         "Std 99 percentile"])

        for op in operation_list:
            for sharded in sharded_list:
                for workers in worker_list:
                    for clients in client_list:
                        cwd = os.path.join(exp_dir,
                                           "ratio_{}".format(op),
                                           "sharded_{}".format(sharded),
                                           "workers_{}".format(workers),
                                           "clients_{}".format(clients))

                        _handle_repetitions(cwd=cwd,
                                            operation=op,
                                            sharded=sharded,
                                            writer=writer)

    outputfile.close()


def _handle_repetitions(cwd,
                        operation,
                        sharded,
                        writer):
    """Handles the innermost repetitions to gather data
    Arguments:
        cwd: path to the working directory of the innermost loop of the experiment
        writer: csv writer linked to outputfile
    """

    tot_data = pd.DataFrame({"25 percentile": [0]*18,
                             "50 percentile": [0]*18,
                             "75 percentile": [0]*18,
                             "90 percentile": [0]*18,
                             "99 percentile": [0]*18})
    location = -1
    for rep in [1, 2, 3]:
        for memtier in range(1, 4):
            for subclient in range(1, 3):
                location += 1
                input_filename = os.path.join(
                    cwd,
                    "client_{}_{}_{}.log".format(memtier, subclient, rep)
                )
                with open(input_filename) as inputfile:
                    passed_25 = False
                    passed_50 = False
                    passed_75 = False
                    passed_90 = False
                    passed_99 = False
                    for line in inputfile.readlines():
                        contents = re.split(r"\s", line)
                        contents = list(filter(None, contents))
                        if len(contents) < 3:
                            continue

                        if contents[0] == "GET" and float(contents[2]) > 25:
                            if not passed_25:
                                tot_data.loc[location] += np.array([float(contents[1]),
                                                                    0,
                                                                    0,
                                                                    0,
                                                                    0])
                            passed_25 = True
                        if contents[0] == "GET" and float(contents[2]) > 50:
                            if not passed_50:
                                tot_data.loc[location] += np.array([0,
                                                                    float(contents[1]),
                                                                    0,
                                                                    0,
                                                                    0])
                            passed_50 = True
                        if contents[0] == "GET" and float(contents[2]) > 75:
                            if not passed_75:
                                tot_data.loc[location] += np.array([0,
                                                                    0,
                                                                    float(contents[1]),
                                                                    0,
                                                                    0])
                            passed_75 = True
                        if contents[0] == "GET" and float(contents[2]) > 90:
                            if not passed_90:
                                tot_data.loc[location] += np.array([0,
                                                                    0,
                                                                    0,
                                                                    float(contents[1]),
                                                                    0])
                            passed_90 = True
                        if contents[0] == "GET" and float(contents[2]) > 99:
                            if not passed_99:
                                tot_data.loc[location] += np.array([0,
                                                                    0,
                                                                    0,
                                                                    0,
                                                                    float(contents[1])])
                            passed_99 = True
                inputfile.close()


    writer.writerow([operation,
                     sharded,
                     tot_data["25 percentile"].mean(),
                     tot_data["25 percentile"].std(),
                     tot_data["50 percentile"].mean(),
                     tot_data["50 percentile"].std(),
                     tot_data["75 percentile"].mean(),
                     tot_data["75 percentile"].std(),
                     tot_data["90 percentile"].mean(),
                     tot_data["90 percentile"].std(),
                     tot_data["99 percentile"].mean(),
                     tot_data["99 percentile"].std()])

if __name__ == "__main__":
    if sys.argv[1] == "all":
        percentiles()
