#!/usr/bin/env python3

import os
import sys
import re
import csv
import pandas as pd
import numpy as np


def preprocess_stab():
    """Preprocesses the data for the stability trace.
    """

    # Check the log directory for logs of with the 2kanalysis
    potential_dirs = os.listdir("/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/" +\
                                "autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs")
    exp_dir = [directory for directory in potential_dirs if not directory.find("2kanalysis")]
    if len(exp_dir) != 1:
        print("Please make sure there is one and only one directory containing " +\
              "'2kanalysis'")
        sys.exit(1)

    exp_dir = os.path.join("/Users/jakob_beckmann/Documents/_uni/eth/_courses/2017/" +\
                           "autumn/advanced_sys_lab/gitlab/asl-fall17-project/logs",
                           exp_dir[0])

    operation_list = ["1:1"]
    mw_count_list = [1]
    server_count_list = [3]
    worker_count_list = [32]

    for mw_count in mw_count_list:
        for server_count in server_count_list:
            for worker_count in worker_count_list:
                for operation in operation_list:
                    cwd = os.path.join(exp_dir,
                                       "mws_{}".format(mw_count),
                                       "servers_{}".format(server_count),
                                       "workers_{}".format(worker_count),
                                       "ratio_{}".format(operation))
                    output_dir = os.path.join("final/stability",
                                              "mws_{}".format(mw_count),
                                              "servers_{}".format(server_count),
                                              "workers_{}".format(worker_count),
                                              "ratio_{}".format(operation))
                    os.makedirs(output_dir)
                    _handle_repetitions(cwd=cwd,
                                        output_dir=output_dir,
                                        mw_count=mw_count)


def _handle_repetitions(cwd,
                        output_dir,
                        mw_count):
    """Handles the repetitions.
    Arguments:
        cwd: current working directory containing the input files
        output_dir: the directory the output files should be stored in
        mw_count: the number of middlewares used in this configuration
    """

    outputfilename = os.path.join(output_dir, "mws.csv")
    with open(outputfilename, 'w', newline="") as outputfile:
        mw_writer = csv.writer(outputfile)
        mw_writer.writerow(["Time",
                            "Average Throughput",
                            "Std Throughput",
                            "Average Latency",
                            "Std Latency",
                            "Average Queue Time",
                            "Std Queue Time",
                            "Average Server Time",
                            "Std Server Time"])
        tot_data = pd.DataFrame({"Latency_1": [0]*80,
                                 "Latency_2": [0]*80,
                                 "Latency_3": [0]*80,
                                 "Queue time_1": [0]*80,
                                 "Queue time_2": [0]*80,
                                 "Queue time_3": [0]*80,
                                 "Server time_1": [0]*80,
                                 "Server time_2": [0]*80,
                                 "Server time_3": [0]*80,
                                 "Throughput_1": [0]*80,
                                 "Throughput_2": [0]*80,
                                 "Throughput_3": [0]*80,
                                 "Time": [0]*80,})
        for rep in [1, 2, 3]:
            rep_data = pd.DataFrame({"Latency": [0]*80,
                                     "Queue time": [0]*80,
                                     "Server time": [0]*80,
                                     "Throughput": [0]*80,
                                     "Time": [0]*80,})
            for mw in range(1, mw_count + 1):
                mw_data = pd.DataFrame({"Latency": [0]*80,
                                        "Queue time": [0]*80,
                                        "Server time": [0]*80,
                                        "Throughput": [0]*80,
                                        "Time": [0]*80,})
                input_filename = os.path.join(
                    cwd,
                    "mw_{}_{}.log".format(mw, rep)
                )
                with open(input_filename) as inputfile:
                    line_num = 0
                    for line in inputfile.readlines():
                        contents = re.split(r"\s", line)
                        contents = list(filter(None, contents))
                        if contents == []:
                            continue
                        if re.match(r"=+", line):
                            break
                        if not (re.match(r"\d+", contents[0].strip()) \
                                or re.match(r"SETS", contents[0])):
                            continue
                        line_num += 1

                        # Skip second line to remove warm up
                        if line_num < 3:
                            continue

                        # Take 80 seconds of measurements
                        if line_num < 83:
                            mw_data.loc[line_num - 3] = np.array([
                                float(contents[6]),
                                float(contents[7]),
                                float(contents[8]),
                                int(contents[4]),
                                line_num - 2,
                            ])
                inputfile.close()

                # Convert timing measurements in ms
                mw_data[["Latency",
                         "Queue time",
                         "Server time"
                        ]] /= 1000

                rep_data += mw_data

            # Get average times and lengths across middlewares
            rep_data[["Latency",
                      "Queue time",
                      "Server time",
                     ]] /= mw_count

            tot_data["Latency_{}".format(rep)] += rep_data["Latency"]
            tot_data["Throughput_{}".format(rep)] += rep_data["Throughput"]
            tot_data["Server time_{}".format(rep)] += rep_data["Server time"]
            tot_data["Queue time_{}".format(rep)] += rep_data["Queue time"]
            tot_data["Time"] = rep_data["Time"]

        for idx in range(1, 81):
            mw_writer.writerow([tot_data["Time"][idx-1],
                                np.mean([tot_data["Throughput_1"][idx-1], tot_data["Throughput_2"][idx-1], tot_data["Throughput_3"][idx-1]]),
                                np.std([tot_data["Throughput_1"][idx-1], tot_data["Throughput_2"][idx-1], tot_data["Throughput_3"][idx-1]]),
                                np.mean([tot_data["Latency_1"][idx-1], tot_data["Latency_2"][idx-1], tot_data["Latency_3"][idx-1]]),
                                np.std([tot_data["Latency_1"][idx-1], tot_data["Latency_2"][idx-1], tot_data["Latency_3"][idx-1]]),
                                np.mean([tot_data["Queue time_1"][idx-1], tot_data["Queue time_2"][idx-1], tot_data["Queue time_3"][idx-1]]),
                                np.std([tot_data["Queue time_1"][idx-1], tot_data["Queue time_2"][idx-1], tot_data["Queue time_3"][idx-1]]),
                                np.mean([tot_data["Server time_1"][idx-1], tot_data["Server time_2"][idx-1], tot_data["Server time_3"][idx-1]]),
                                np.std([tot_data["Server time_1"][idx-1], tot_data["Server time_2"][idx-1], tot_data["Server time_3"][idx-1]]),])

    outputfile.close()


if __name__ == "__main__":
    if sys.argv[1] == "all":
        preprocess_stab()
