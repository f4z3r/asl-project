#!/usr/bin/env python3

import os
import sys
import re
import csv
import pandas as pd
import numpy as np

VALID_LINE = re.compile(r"\[RUN #1\s+\d+%,\s+\d+ secs\]")


def preprocess(name,
               memtier_count,
               mw_count,
               operation_list,
               sharded_list,
               worker_list,
               client_list,
               subclient_count):
    """Preprocesses the data for a given experiment.
    Arguments:
        name: String of the experiment name
        memtier_count: number of memtier machines used in the experiment
        mw_count: number of mw machiens used in the experiment
        operation_list: list of ratios used in the experiment
        sharded_list: list of sharding parameters
        worker_list: list of worker numbers used in experiment
        client_list: list of client numbers per thread used in experiment
        subclient_list: list of subclients used by memtier in experiment
    """

    # Check the log directory for logs of with the name of the experiment
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

    for op in operation_list:
        for sharded in sharded_list:
            for workers in worker_list:
                for clients in client_list:
                    cwd = os.path.join(exp_dir,
                                       "ratio_{}".format(op),
                                       "sharded_{}".format(sharded),
                                       "workers_{}".format(workers),
                                       "clients_{}".format(clients))

                    # Create a directory for the processed results
                    output_dir = os.path.join("processed",
                                              name,
                                              "ratio_{}".format(op),
                                              "sharded_{}".format(sharded),
                                              "workers_{}".format(workers),
                                              "clients_{}".format(clients))
                    os.makedirs(output_dir)
                    clients_filename = os.path.join(output_dir, "clients.csv")
                    with open(clients_filename, 'w', newline="") as clients_file:
                        client_writer = csv.writer(clients_file)

                        if mw_count != 0:
                            mw_filename = os.path.join(output_dir, "mws.csv")
                            with open(mw_filename, 'w', newline="") as mw_file:
                                mw_writer = csv.writer(mw_file)
                                _handle_repetitions(cwd=cwd,
                                                    memtier_count=memtier_count,
                                                    subclient_count=subclient_count,
                                                    client_writer=client_writer,
                                                    mw_count=mw_count,
                                                    mw_writer=mw_writer)
                            mw_file.close()
                        else:
                            _handle_repetitions(cwd=cwd,
                                                memtier_count=memtier_count,
                                                subclient_count=subclient_count,
                                                client_writer=client_writer)

                    clients_file.close()






def _handle_repetitions(cwd,
                        memtier_count,
                        subclient_count,
                        client_writer,
                        mw_count=0,
                        mw_writer=None):
    """Handles the innermost repetitions to gather data
    Arguments:
        cwd: path to the working directory of the innermost loop of the experiment
        memtier_count: count of memtier machines used in experiment
        subclient_count: count of subclients used on each memtier machine
        client_writer: csv writer to write client output to
        mw_count: number of middlewares used in experiments
        mw_writer: csv wirter to write mw output to
    """

    client_writer.writerow(["Repetition",
                            "Client",
                            "Subclient",
                            "Average Throughput",
                            "Std Throughput",
                            "Average Latency",
                            "Std Latency"])

    tot_data = pd.DataFrame({"Latency": [0]*80, "Throughput": [0]*80})
    for rep in [1, 2, 3]:
        rep_data = pd.DataFrame({"Latency": [0]*80, "Throughput": [0]*80})
        for memtier in range(1, memtier_count + 1):
            memtier_data = pd.DataFrame({"Latency": [0]*80, "Throughput": [0]*80})
            for subclient in range(1, subclient_count + 1):
                subclient_data = pd.DataFrame({"Latency": [0]*80, "Throughput": [0]*80})
                input_filename = os.path.join(
                    cwd,
                    "client_{}_{}_{}.log".format(memtier, subclient, rep)
                )
                with open(input_filename) as inputfile:
                    line_num = 0
                    for content in inputfile.readlines():
                        content.strip()

                        # Check if it is a valid line
                        if re.match(VALID_LINE, content):
                            lines = content.split("\r")
                            for line in lines:
                                line.strip()

                                line_num += 1

                                # Don't print first 8 lines to remove warm up time
                                if line_num < 9:
                                    continue

                                # Take 80 seconds of measurements
                                if line_num < 89:
                                    line_content = re.split(r"\s", line)
                                    line_content = list(filter(None, line_content))
                                    subclient_data.loc[line_num - 9] = np.array([
                                        float(line_content[16]),
                                        int(line_content[9]),
                                    ])
                inputfile.close()
                client_writer.writerow([rep,
                                        memtier,
                                        subclient,
                                        subclient_data["Throughput"].mean(),
                                        subclient_data["Throughput"].std(),
                                        subclient_data["Latency"].mean(),
                                        subclient_data["Latency"].std()])

                memtier_data += subclient_data

            # Get average latency across subclients
            memtier_data["Latency"] /= subclient_count
            client_writer.writerow([rep,
                                    memtier,
                                    "Total",
                                    memtier_data["Throughput"].mean(),
                                    memtier_data["Throughput"].std(),
                                    memtier_data["Latency"].mean(),
                                    memtier_data["Latency"].std()])
            rep_data += memtier_data

        # Get average latency across clients
        rep_data["Latency"] /= memtier_count
        client_writer.writerow([rep,
                                "Total",
                                "Total",
                                rep_data["Throughput"].mean(),
                                rep_data["Throughput"].std(),
                                rep_data["Latency"].mean(),
                                rep_data["Latency"].std()])
        tot_data += rep_data

    # Get average across all reps
    tot_data /= 3
    client_writer.writerow(["Total",
                            "Total",
                            "Total",
                            tot_data["Throughput"].mean(),
                            tot_data["Throughput"].std(),
                            tot_data["Latency"].mean(),
                            tot_data["Latency"].std()])

    # Check if we need to handle middleware info
    if mw_count == 0:
        return

    if mw_writer is None:
        print("Please provide a middleware writer when handling middlewares, " +\
              "proceeding without using middleware data.")
        return

    mw_writer.writerow(["Repetition",
                        "Middleware",
                        "Average Throughput",
                        "Std Throughput",
                        "Average Latency",
                        "Std Latency",
                        "Average Gets",
                        "Average Multigets",
                        "Average Sets",
                        "Average Invalids",
                        "Average Hits",
                        "Average Queue Length",
                        "Std Queue Length",
                        "Average Queue Time",
                        "Std Queue Time",
                        "Average Server Time",
                        "Std Server Time"])
    tot_data = pd.DataFrame({"Gets": [0]*80,
                             "Hits": [0]*80,
                             "Invalids": [0]*80,
                             "Latency": [0]*80,
                             "Multigets": [0]*80,
                             "Queue length": [0]*80,
                             "Queue time": [0]*80,
                             "Server time": [0]*80,
                             "Sets": [0]*80,
                             "Total": [0]*80,})
    for rep in [1, 2, 3]:
        rep_data = pd.DataFrame({"Gets": [0]*80,
                                 "Hits": [0]*80,
                                 "Invalids": [0]*80,
                                 "Latency": [0]*80,
                                 "Multigets": [0]*80,
                                 "Queue length": [0]*80,
                                 "Queue time": [0]*80,
                                 "Server time": [0]*80,
                                 "Sets": [0]*80,
                                 "Total": [0]*80,})
        for mw in range(1, mw_count + 1):
            mw_data = pd.DataFrame({"Gets": [0]*80,
                                    "Hits": [0]*80,
                                    "Invalids": [0]*80,
                                    "Latency": [0]*80,
                                    "Multigets": [0]*80,
                                    "Queue length": [0]*80,
                                    "Queue time": [0]*80,
                                    "Server time": [0]*80,
                                    "Sets": [0]*80,
                                    "Total": [0]*80,})
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
                            int(contents[1]),
                            int(contents[5]),
                            int(contents[3]),
                            float(contents[6]),
                            int(contents[2]),
                            int(contents[9]),
                            float(contents[7]),
                            float(contents[8]),
                            int(contents[0]),
                            int(contents[4]),
                        ])
            inputfile.close()

            # Convert timing measurements in ms
            mw_data[["Latency",
                     "Queue time",
                     "Server time"
                    ]] /= 1000

            mw_writer.writerow([rep,
                                mw,
                                mw_data["Total"].mean(),
                                mw_data["Total"].std(),
                                mw_data["Latency"].mean(),
                                mw_data["Latency"].std(),
                                mw_data["Gets"].mean(),
                                mw_data["Multigets"].mean(),
                                mw_data["Sets"].mean(),
                                mw_data["Invalids"].mean(),
                                mw_data["Hits"].mean(),
                                mw_data["Queue length"].mean(),
                                mw_data["Queue length"].std(),
                                mw_data["Queue time"].mean(),
                                mw_data["Queue time"].std(),
                                mw_data["Server time"].mean(),
                                mw_data["Server time"].std()])

            rep_data += mw_data

        # Get average times and lengths across middlewares
        rep_data[["Latency",
                  "Queue length",
                  "Queue time",
                  "Server time",
                 ]] /= mw_count

        mw_writer.writerow([rep,
                            "Total",
                            rep_data["Total"].mean(),
                            rep_data["Total"].std(),
                            rep_data["Latency"].mean(),
                            rep_data["Latency"].std(),
                            rep_data["Gets"].mean(),
                            rep_data["Multigets"].mean(),
                            rep_data["Sets"].mean(),
                            rep_data["Invalids"].mean(),
                            rep_data["Hits"].mean(),
                            rep_data["Queue length"].mean(),
                            rep_data["Queue length"].std(),
                            rep_data["Queue time"].mean(),
                            rep_data["Queue time"].std(),
                            rep_data["Server time"].mean(),
                            rep_data["Server time"].std()])
        tot_data += rep_data

    # Get average across all repetitions
    tot_data /= 3
    mw_writer.writerow(["Total",
                        "Total",
                        tot_data["Total"].mean(),
                        tot_data["Total"].std(),
                        tot_data["Latency"].mean(),
                        tot_data["Latency"].std(),
                        tot_data["Gets"].mean(),
                        tot_data["Multigets"].mean(),
                        tot_data["Sets"].mean(),
                        tot_data["Invalids"].mean(),
                        tot_data["Hits"].mean(),
                        tot_data["Queue length"].mean(),
                        tot_data["Queue length"].std(),
                        tot_data["Queue time"].mean(),
                        tot_data["Queue time"].std(),
                        tot_data["Server time"].mean(),
                        tot_data["Server time"].std()])



if __name__ == "__main__":
    if sys.argv[1] == "all":
        preprocess(name="benchmark_memcached",
                   memtier_count=3,
                   mw_count=0,
                   operation_list=["0:1", "1:0"],
                   sharded_list=["false"],
                   worker_list=["no"],
                   client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56],
                   subclient_count=1)
        preprocess(name="benchmark_clients",
                   memtier_count=1,
                   mw_count=0,
                   operation_list=["0:1", "1:0"],
                   sharded_list=["false"],
                   worker_list=["no"],
                   client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56],
                   subclient_count=2)
        preprocess(name="benchmark_1mw",
                   memtier_count=1,
                   mw_count=1,
                   operation_list=["0:1", "1:0"],
                   sharded_list=["false"],
                   worker_list=[8, 16, 32, 64],
                   client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56],
                   subclient_count=1)
        preprocess(name="benchmark_2mw",
                   memtier_count=1,
                   mw_count=2,
                   operation_list=["0:1", "1:0"],
                   sharded_list=["false"],
                   worker_list=[8, 16, 32, 64],
                   client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56],
                   subclient_count=2)
        preprocess(name="throughput_writes",
                   memtier_count=3,
                   mw_count=2,
                   operation_list=["1:0"],
                   sharded_list=["false"],
                   worker_list=[8, 16, 32, 64],
                   client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56],
                   subclient_count=2)
        preprocess(name="get_and_multigets",
                   memtier_count=3,
                   mw_count=2,
                   operation_list=["0:9", "0:6", "0:3", "0:1"],
                   sharded_list=["true", "false"],
                   worker_list=[64],
                   client_list=[2],
                   subclient_count=2)
