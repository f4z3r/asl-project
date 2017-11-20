#!/usr/bin/env python3

import sys
import os
import csv
import re
import pandas as pd
import numpy as np

def handle_dstat(name,
                 memtier_count,
                 mw_count,
                 server_count,
                 operation_list,
                 sharded_list,
                 worker_list,
                 client_list):
    """Handles all dstat data from experiments:
    Arguments:
        name: string name of the experiment name
        memtier_count: integer count of memtier machines used in experiment
        mw_count: integer count of middlewares used in experiment
        server_count: integer count of servers used in experiment
        operation_list: list of operations used in experiment
        sharded_list: list of sharded parameters used in experiment
        worker_list: list of worker counts used in the experiment
        client_list: list of client counts used in the experiment"""

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

    output_dir = os.path.join("processed", name)
    try:
        os.makedirs(output_dir)
    except:
        pass
    outputfilename = os.path.join(output_dir, "dstat.csv")
    with open(outputfilename, 'w', newline="") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(["Operation",
                         "Sharded",
                         "Workers",
                         "Clients",
                         "Machine type",
                         "Machine number",
                         "Average CPU usage",
                         "Std CPU usage",
                         "Average Network receive",
                         "Std Network receive",
                         "Average Network write",
                         "Std Network write"])

        for op in operation_list:
            for sharded in sharded_list:
                for workers in worker_list:
                    for clients in client_list:
                        cwd = os.path.join(exp_dir,
                                           "ratio_{}".format(op),
                                           "sharded_{}".format(sharded),
                                           "workers_{}".format(workers),
                                           "clients_{}".format(clients),
                                           "dstat")
                        _handle_inner_loop(operation=op,
                                           sharded=sharded,
                                           workers=workers,
                                           clients=clients,
                                           memtier_count=memtier_count,
                                           mw_count=mw_count,
                                           server_count=server_count,
                                           cwd=cwd,
                                           writer=writer)

    outputfile.close()


def _handle_inner_loop(operation,
                       sharded,
                       workers,
                       clients,
                       memtier_count,
                       mw_count,
                       server_count,
                       cwd,
                       writer):
    """Handles the data aggregation for a single configuration setup.
    Arguments:
        operation: operation used in this configuration
        sharded: sharded parameter used in this configuration
        workers: worker count used in this configuration
        clients: client count used in this configuration
        memtier_count: integer count of memtier machines used in the experiment
        mw_count: integer count of middleware machines used in the experiment
        server_count: integer count of server machines used in the experiment
        cwd: directory containing dstat files for current configuration
        write: writer linked to output file"""

    tot_data = pd.DataFrame({"CPU usage": [0]*80,
                             "Network receive": [0]*80,
                             "Network write": [0]*80})

    for mw in range(1, mw_count + 1):
        data = pd.DataFrame({"CPU usage": [0]*80,
                             "Network receive": [0]*80,
                             "Network write": [0]*80})
        for rep in [1, 2, 3]:
            rep_data = pd.DataFrame({"CPU usage": [0]*80,
                                     "Network receive": [0]*80,
                                     "Network write": [0]*80})

            inputfilename = os.path.join(cwd, "dstat_mw_{}_{}.log".format(mw, rep))
            with open(inputfilename, 'r') as inputfile:
                line_num = 0
                for line in inputfile.readlines():
                    line_num += 1
                    if line_num < 11:
                        continue
                    if line_num > 90:
                        break
                    content = re.split(r"[\s|]", line)
                    content = list(filter(None, content))
                    rep_data.loc[line_num - 11] = np.array([
                        100 - int(content[2]),
                        int(content[6].replace("k", "000").replace("M", "000000").replace("B", "")),
                        int(content[7].replace("k", "000").replace("M", "000000").replace("B", ""))
                    ])
            inputfile.close()
            data += rep_data

        data /= 3
        writer.writerow([operation,
                         sharded,
                         workers,
                         clients,
                         "mw",
                         mw,
                         data["CPU usage"].mean(),
                         data["CPU usage"].std(),
                         data["Network receive"].mean(),
                         data["Network receive"].std(),
                         data["Network write"].mean(),
                         data["Network write"].std()])
        tot_data += data

    if mw_count > 0:
        tot_data /= mw_count
        writer.writerow([operation,
                         sharded,
                         workers,
                         clients,
                         "mw",
                         "total",
                         tot_data["CPU usage"].mean(),
                         tot_data["CPU usage"].std(),
                         tot_data["Network receive"].mean(),
                         tot_data["Network receive"].std(),
                         tot_data["Network write"].mean(),
                         tot_data["Network write"].std()])

    tot_data = pd.DataFrame({"CPU usage": [0]*80,
                             "Network receive": [0]*80,
                             "Network write": [0]*80})

    for memtier in range(1, memtier_count + 1):
        data = pd.DataFrame({"CPU usage": [0]*80,
                             "Network receive": [0]*80,
                             "Network write": [0]*80})
        for rep in [1, 2, 3]:
            rep_data = pd.DataFrame({"CPU usage": [0]*80,
                                     "Network receive": [0]*80,
                                     "Network write": [0]*80})

            inputfilename = os.path.join(cwd, "dstat_client_{}_{}.log".format(memtier, rep))
            with open(inputfilename, 'r') as inputfile:
                line_num = 0
                for line in inputfile.readlines():
                    line_num += 1
                    if line_num < 9:
                        continue
                    if line_num > 88:
                        break
                    content = re.split(r"[\s|]", line)
                    content = list(filter(None, content))
                    rep_data.loc[line_num - 11] = np.array([
                        100 - int(content[2]),
                        int(content[6].replace("k", "000").replace("M", "000000").replace("B", "")),
                        int(content[7].replace("k", "000").replace("M", "000000").replace("B", ""))
                    ])
            inputfile.close()
            data += rep_data

        data /= 3
        writer.writerow([operation,
                         sharded,
                         workers,
                         clients,
                         "client",
                         memtier,
                         data["CPU usage"].mean(),
                         data["CPU usage"].std(),
                         data["Network receive"].mean(),
                         data["Network receive"].std(),
                         data["Network write"].mean(),
                         data["Network write"].std()])
        tot_data += data
    tot_data /= memtier_count
    writer.writerow([operation,
                     sharded,
                     workers,
                     clients,
                     "client",
                     "total",
                     tot_data["CPU usage"].mean(),
                     tot_data["CPU usage"].std(),
                     tot_data["Network receive"].mean(),
                     tot_data["Network receive"].std(),
                     tot_data["Network write"].mean(),
                     tot_data["Network write"].std()])

    tot_data = pd.DataFrame({"CPU usage": [0]*80,
                             "Network receive": [0]*80,
                             "Network write": [0]*80})

    for server in range(1, server_count + 1):
        data = pd.DataFrame({"CPU usage": [0]*80,
                             "Network receive": [0]*80,
                             "Network write": [0]*80})
        for rep in [1, 2, 3]:
            rep_data = pd.DataFrame({"CPU usage": [0]*80,
                                     "Network receive": [0]*80,
                                     "Network write": [0]*80})

            inputfilename = os.path.join(cwd, "dstat_server_{}_{}.log".format(server, rep))
            with open(inputfilename, 'r') as inputfile:
                line_num = 0
                for line in inputfile.readlines():
                    line_num += 1
                    if line_num < 9:
                        continue
                    if line_num > 88:
                        break
                    content = re.split(r"[\s|]", line)
                    content = list(filter(None, content))
                    rep_data.loc[line_num - 11] = np.array([
                        100 - int(content[2]),
                        int(content[6].replace("k", "000").replace("M", "000000").replace("B", "")),
                        int(content[7].replace("k", "000").replace("M", "000000").replace("B", ""))
                    ])
            inputfile.close()
            data += rep_data

        data /= 3
        writer.writerow([operation,
                         sharded,
                         workers,
                         clients,
                         "server",
                         server,
                         data["CPU usage"].mean(),
                         data["CPU usage"].std(),
                         data["Network receive"].mean(),
                         data["Network receive"].std(),
                         data["Network write"].mean(),
                         data["Network write"].std()])
        tot_data += data
    tot_data /= server_count
    writer.writerow([operation,
                     sharded,
                     workers,
                     clients,
                     "server",
                     "total",
                     tot_data["CPU usage"].mean(),
                     tot_data["CPU usage"].std(),
                     tot_data["Network receive"].mean(),
                     tot_data["Network receive"].std(),
                     tot_data["Network write"].mean(),
                     tot_data["Network write"].std()])

if __name__ == "__main__":
    if sys.argv[1] == "all":
        handle_dstat(name="benchmark_memcached",
                     memtier_count=3,
                     mw_count=0,
                     server_count=1,
                     operation_list=["0:1", "1:0"],
                     sharded_list=["false"],
                     worker_list=["no"],
                     client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56])
        handle_dstat(name="benchmark_clients",
                     memtier_count=1,
                     mw_count=0,
                     server_count=2,
                     operation_list=["0:1", "1:0"],
                     sharded_list=["false"],
                     worker_list=["no"],
                     client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56])
        handle_dstat(name="benchmark_1mw",
                     memtier_count=1,
                     mw_count=1,
                     server_count=1,
                     operation_list=["0:1", "1:0"],
                     sharded_list=["false"],
                     worker_list=[8, 16, 32, 64],
                     client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56])
        handle_dstat(name="benchmark_2mw",
                     memtier_count=1,
                     mw_count=2,
                     server_count=1,
                     operation_list=["0:1", "1:0"],
                     sharded_list=["false"],
                     worker_list=[8, 16, 32, 64],
                     client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56])
        handle_dstat(name="throughput_writes",
                     memtier_count=3,
                     mw_count=2,
                     server_count=3,
                     operation_list=["1:0"],
                     sharded_list=["false"],
                     worker_list=[8, 16, 32, 64],
                     client_list=[2, 4, 8, 16, 24, 32, 40, 48, 56])
        handle_dstat(name="get_and_multigets",
                     memtier_count=3,
                     mw_count=2,
                     server_count=3,
                     operation_list=["0:1", "0:3", "0:6", "0:9"],
                     sharded_list=["true", "false"],
                     worker_list=[64],
                     client_list=[2])
