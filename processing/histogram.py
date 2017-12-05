#!/usr/bin/env python3


import sys
import os
import csv
import re
import pandas as pd
import numpy as np

def histogram():
    """Gathers client percentile information."""

    # Config
    name = "get_and_multigets"
    operation_list = ["0:6"]
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
    outputfilename = os.path.join(output_dir, "histograms.csv")

    with open(outputfilename, 'w', newline="") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow([name.upper()])
        writer.writerow(["Histograms"])
        writer.writerow([])

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
                                            sharded=sharded,
                                            writer=writer)

    outputfile.close()


def _handle_repetitions(cwd,
                        sharded,
                        writer):
    """Handles the innermost repetitions to gather data
    Arguments:
        cwd: path to the working directory of the innermost loop of the experiment
        writer: csv writer linked to outputfile
    """

    # Client data
    tot_data = pd.DataFrame({"Histogram": [0] * 66})
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
                    prev_percent = .0
                    for line in inputfile.readlines():
                        contents = re.split(r"\s", line)
                        contents = list(filter(None, contents))
                        if len(contents) < 3:
                            continue

                        if contents[0] == "GET":
                            time = float(contents[1])
                            if time > 6.999:
                                tot_data.loc[65] += np.array([100 - prev_percent])
                                break

                            if time < 6.999 and time > 0.499:
                                percent = float(contents[2])
                                location = int((time - 0.499) * 10)
                                tot_data.loc[location] += np.array([percent - prev_percent])
                                prev_percent = percent

                inputfile.close()
    tot_data /= 18

    writer.writerow([])
    writer.writerow([])
    writer.writerow(["sharded: {}, clients".format(sharded)])
    time = 0.4
    for row in tot_data["Histogram"]:
        writer.writerow([time, row])
        time += 0.1


    # Middleware data
    tot_data = pd.DataFrame({"Histogram": [0] * 66})
    location = -1
    for rep in [1, 2, 3]:
        for mw in range(1, 3):
            location += 1
            input_filename = os.path.join(
                cwd,
                "mw_{}_{}.log".format(mw, rep)
            )
            with open(input_filename) as inputfile:
                prev_percent = .0
                for line in inputfile.readlines():
                    contents = re.split(r"\s", line)
                    contents = list(filter(None, contents))
                    if len(contents) == 2:
                        try:
                            time = float(contents[0])
                            percent = float(contents[1].strip("%"))
                        except:
                            # Not correct types (i.e. not histogram)
                            continue
                        if time > 6.999:
                            tot_data.loc[65] += np.array([100 - prev_percent])
                            break

                        if time < 6.999 and time > 0.499:
                            location = int((time - 0.499) * 10)
                            tot_data.loc[location] += np.array([percent - prev_percent])
                            prev_percent = percent
            inputfile.close()
    tot_data /= 6

    writer.writerow([])
    writer.writerow([])
    writer.writerow(["sharded: {}, middlewares".format(sharded)])
    time = 0.4
    for row in tot_data["Histogram"]:
        writer.writerow([time, row])
        time += 0.1

if __name__ == "__main__":
    if sys.argv[1] == "all":
        histogram()
