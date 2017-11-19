#!/usr/bin/env python3

import sys
import os
import csv
import pandas as pd
import numpy as np

def aggregate(name,
              operation_list,
              sharded_list,
              worker_list,
              client_list,
              mw=True):
    """Aggregates all files within the processed directory for that experiment and produce a single
    file used for graphing etc.
    Arguments:
        name: String of the experiment name
        memtier_count: integer count of memtier machines in experiment
        mw_count: integer count of middlewares used in experiment
        operation_list: list of operations used in experiment
        sharded_list: list of sharding parameters used in experiment
        worker_list: list of worker parameters used in experiment
        client_list: list of clients used in experiment
        mw=True: whether this experiment used middlewares"""

    cwd = os.path.join("final", name)
    os.makedirs(cwd)

    with open(os.path.join(cwd, "data.csv"), 'w', newline="") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow([name.upper()])
        writer.writerow([])
        writer.writerow([])

        writer.writerow(["Operation",
                         "Sharded",
                         "Workers",
                         "Clients",
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

        for op in operation_list:
            for sharded in sharded_list:
                for workers in worker_list:
                    for clients in client_list:
                        input_dir = os.path.join("processed",
                                                 name,
                                                 "ratio_{}".format(op),
                                                 "sharded_{}".format(sharded),
                                                 "workers_{}".format(workers),
                                                 "clients_{}".format(clients))
                        _handle_innerloop(operation=op,
                                          sharded=sharded,
                                          workers=workers,
                                          clients=clients,
                                          input_dir=input_dir,
                                          writer=writer,
                                          mw=mw)



def _handle_innerloop(operation,
                      sharded,
                      workers,
                      clients,
                      input_dir,
                      writer,
                      mw=True):
    """Handles printing a single row of aggregate data from one configuration within an
    experiment.
    Arguments:
        operation: the operation of the current configuration
        sharded: the sharded parameters of the current configuration
        workers: the worker count used in the current configuration
        clients: the client count used in the current configuration
        input_dir: the directory containing the input files of the current configuration
        writer: the CSV writer object linked to the ouput file for this experiment
        mw=True: whether this experiment used middlewares."""

    rep_data = pd.DataFrame({"Latency (clients)": [0]*3,
                             "Latency (mw)": [0]*3,
                             "Throughput (clients)": [0]*3,
                             "Throughput (mw)": [0]*3})
    data = [operation, sharded, workers, clients]

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

    if mw is True:
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
    else:
        data += [0] * 11

    data += ["",
             rep_data["Throughput (clients)"].std(),
             rep_data["Latency (clients)"].std(),
             rep_data["Throughput (mw)"].std(),
             rep_data["Latency (mw)"].std()]


    writer.writerow(data)


if __name__ == "__main__":
    if sys.argv[1] == "all":
        aggregate(name="benchmark_memcached",
                  operation_list=["0:1", "1:0"],
                  sharded_list=["false"],
                  worker_list=["no"],
                  client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56],
                  mw=False)
        aggregate(name="benchmark_clients",
                  operation_list=["0:1", "1:0"],
                  sharded_list=["false"],
                  worker_list=["no"],
                  client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56],
                  mw=False)
        aggregate(name="benchmark_1mw",
                  operation_list=["0:1", "1:0"],
                  sharded_list=["false"],
                  worker_list=[8, 16, 32, 64],
                  client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56])
        aggregate(name="benchmark_2mw",
                  operation_list=["0:1", "1:0"],
                  sharded_list=["false"],
                  worker_list=[8, 16, 32, 64],
                  client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56])
        aggregate(name="throughput_writes",
                  operation_list=["1:0"],
                  sharded_list=["false"],
                  worker_list=[8, 16, 32, 64],
                  client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56])
        aggregate(name="get_and_multigets",
                  operation_list=["0:9", "0:6", "0:3", "0:1"],
                  sharded_list=["true", "false"],
                  worker_list=[64],
                  client_list=[2])
