#!/usr/bin/env python3


import sys
import os
import csv
import pandas as pd
import numpy as np

def aggregate_2k():
    """Aggregates all files within the processed directory for 2k analysis and produce a
    single file
    """

    cwd = os.path.join("final", "2kanalysis")
    try:
        os.makedirs(cwd)
    except:
        pass

    operation_list = ["1:0", "0:1", "1:1"]
    mw_count_list = [1, 2]
    server_count_list = [2, 3]
    worker_count_list = [8, 32]

    with open(os.path.join(cwd, "data.csv"), 'w', newline="") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(["2K_ANALYSIS"])
        writer.writerow([])
        writer.writerow([])

        writer.writerow(["Middleware count",
                         "Server count",
                         "Worker count",
                         "Operation",
                         "Average Throughput (client)",
                         "Std Throughtput (client)",
                         "Average Latency (client)",
                         "Std Latency (client)",
                         "Average Throughput (mw)",
                         "Std Throughput (mw)",
                         "Average Latency (mw)",
                         "Std Latency (mw)",
                         "Average Queue Length (mw)",
                         "Std Queue Length (mw)",
                         "Average Queue Time (mw)",
                         "Std Queue Time (mw)",
                         "Average Server Time (mw)",
                         "Std Server Time (mw)",
                         "Hits/Throughput (mw)",
                         "",
                         "Std Throughput across reps (clients)",
                         "Std Latency across reps (clients)",
                         "Std Throughtput across reps (mw)",
                         "Std Latency across reps (mw)"])

        for mw_count in mw_count_list:
            for server_count in server_count_list:
                for worker_count in worker_count_list:
                    for operation in operation_list:
                        input_dir = os.path.join("processed/2kanalysis",
                                                 "mws_{}".format(mw_count),
                                                 "servers_{}".format(server_count),
                                                 "workers_{}".format(worker_count),
                                                 "ratio_{}".format(operation))
                        _handle_innerloop(mw_count=mw_count,
                                          server_count=server_count,
                                          worker_count=worker_count,
                                          operation=operation,
                                          input_dir=input_dir,
                                          writer=writer)


def _handle_innerloop(mw_count,
                      server_count,
                      worker_count,
                      operation,
                      input_dir,
                      writer):
    """Handles printing a single row of aggregate data from one configuration.
    Arguments:
        mw_count: number of middlewares used in this configuration
        server_count: number of servers used in this configuration
        worker_count: number of workers used in this configuration
        operation: operation used in this configuration
        input_dir: directory containing the input files
        writer: csv writer linked to the ouput file
        """

    rep_data = pd.DataFrame({"Latency (clients)": [0]*3,
                             "Latency (mw)": [0]*3,
                             "Throughput (clients)": [0]*3,
                             "Throughput (mw)": [0]*3})
    data = [mw_count, server_count, worker_count, operation]
    with open(os.path.join(input_dir, "clients.csv"), 'r', newline="") as clientfile:
        clientreader = csv.reader(clientfile)

        for content in clientreader:
            if content[1:3] == ["Total", "Total"] and content[0] != "Total":
                rep_data.loc[int(content[0]) - 1] += np.array([float(content[5]),
                                                               0,
                                                               float(content[3]),
                                                               0])
            if content[:3] == ["Total", "Total", "Total"]:
                data += content[3:]

    clientfile.close()
    with open(os.path.join(input_dir, "mws.csv"), 'r', newline="") as mwfile:
        mwreader = csv.reader(mwfile)

        for content in mwreader:
            if content[1] == "Total" and content[0] != "Total":
                rep_data.loc[int(content[0]) - 1] += np.array([0,
                                                               float(content[4]),
                                                               0,
                                                               float(content[2])])
            if content[:2] == ["Total", "Total"]:
                data += content[2:6] + content[11:] + [float(content[10]) / float(content[2])]

    mwfile.close()

    data += ["",
             rep_data["Throughput (clients)"].std(),
             rep_data["Latency (clients)"].std(),
             rep_data["Throughput (mw)"].std(),
             rep_data["Latency (mw)"].std()]

    writer.writerow(data)

if __name__ == "__main__":
    if sys.argv[1] == "all":
        aggregate_2k()
