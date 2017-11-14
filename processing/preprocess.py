#!/usr/bin/env python3

import os
import sys
import re
import csv

valid_line = re.compile(r"\[RUN #1\s+\d+%,\s+\d+ secs\]")

def preprosses_memtier(experiment_name, client_count, thread_count):
    """Docstring"""

    sub_clients = False
    has_workers = True
    if re.search(r"bench_memcached", experiment_name):
        experiment = "bench_memcached"
        has_workers = False
    elif re.search(r"bench_clients", experiment_name):
        experiment = "bench_clients"
        sub_clients = True
        has_workers = False
    elif re.search(r"bench_1mw", experiment_name):
        experiment = "bench_1mw"
    elif re.search(r"bench_2mw", experiment_name):
        experiment = "bench_2mw"
        sub_clients = True

    for operation in ["read", "write"]:
        for workers in [8, 16, 32, 64]:
            if not has_workers and workers != 8:
                continue
            if has_workers:
                client_list = [2, 4, 8, 14, 20, 26, 32]
            else:
                client_list = [1, 2, 4, 8, 16, 24, 32]
            for nclients in client_list:
                if has_workers:
                    cwd = "preprocessed/{}/{}/{}_workers/{}_clients".format(experiment, operation, workers, nclients)
                else:
                    cwd = "preprocessed/{}/{}/{}_clients".format(experiment, operation, nclients)
                for client in range(1, client_count + 1):
                    os.makedirs("{}/client{}".format(cwd, client))
                    for rep in range(1, 4):
                        with open("{}/client{}/rep{}.csv".format(cwd, client, rep), 'w') as writefile:
                            writer = csv.writer(writefile)
                            writer.writerow(["Throughput", "Latency"])
                            if sub_clients:
                                filename = "../logs/{}/{}threads_{}clients_{}/clients/client1-{}_{}.log".format(experiment_name, thread_count, nclients, operation, client, rep)
                            if not has_workers:
                                if sub_clients:
                                    filename = "../logs/{}/{}threads_{}clients_{}/clients/client1-{}_{}.log".format(experiment_name, thread_count, nclients, operation, client, rep)
                                else:
                                    filename = "../logs/{}/{}threads_{}clients_{}/clients/client{}_{}.log".format(experiment_name, thread_count, nclients, operation, client, rep)
                            else:
                                if sub_clients:
                                    filename = "../logs/{}/{}_workers/{}threads_{}clients_{}/clients/client1-{}_{}.log".format(experiment_name, workers, thread_count, nclients, operation, client, rep)
                                else:
                                    filename = "../logs/{}/{}_workers/{}threads_{}clients_{}/clients/client{}_{}.log".format(experiment_name, workers, thread_count, nclients, operation, client, rep)
                            with open(filename, 'r') as readfile:
                                line_num = 0
                                for content in readfile.readlines():
                                    content.strip()

                                    # Check if valid line
                                    if re.match(valid_line, content):
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
                                                writer.writerow([int(line_content[9]), float(line_content[16])])

                                readfile.close()
                        writefile.close()


def preproce_middleware(experiment_name, mw_count, thread_count):
    """Docstring"""

    if re.search(r"bench_1mw", experiment_name):
        experiment = "bench_1mw"
    elif re.search(r"bench_2mw", experiment_name):
        experiment = "bench_2mw"

    for operation in ["read", "write"]:
        for nworkers in [8, 16, 32, 64]:
            for nclients in [2, 4, 8, 14, 20, 26, 32]:
                for mw in range(1, mw_count + 1):
                    cwd = "preprocessed/{}/{}/{}_workers/{}_clients/mw{}".format(experiment, operation, nworkers, nclients, mw)
                    os.makedirs(cwd)
                    for rep in range(1, 4):
                        with open("{}/rep{}.csv".format(cwd, rep), 'w') as writefile:
                            writer = csv.writer(writefile)
                            writer.writerow(["SETS", "GETS", "MGETS", "INVLD", "TOT", "HITS", "RSP T", "Q T", "SVR T", "Q LEN"])
                            with open("../logs/{}/{}_workers/{}threads".format(experiment_name, nworkers, thread_count) +\
                                    "_{}clients_{}/mw/mw{}_{}.log".format(nclients, operation, mw, rep), 'r') as readfile:
                                line_num = 0
                                for line in readfile.readlines():
                                    # Check if line is valid
                                    contents = re.split(r"\s", line)
                                    contents = list(filter(None, contents))
                                    if contents == []:
                                        continue
                                    if re.match(r"=+", line):
                                        break
                                    if not (re.match(r"\d+", contents[0].strip()) or re.match(r"SETS", contents[0])):
                                        continue
                                    line_num += 1

                                    # Skip second line to remove warm up
                                    if line_num < 3:
                                        continue

                                    # Take 80 seconds of measurements
                                    if line_num < 83:
                                        writer.writerow(contents)
                            readfile.close()
                        writefile.close()





if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == "all":
                preprosses_memtier("2017-11-11_17h12(bench_memcached)", 3, 2)
                preprosses_memtier("2017-11-11_18h21(bench_clients)", 2, 1)
                preprosses_memtier("2017-11-12_16h58(bench_1mw)", 1, 2)
                preproce_middleware("2017-11-12_16h58(bench_1mw)", 1, 2)
                preprosses_memtier("2017-11-13_18h55(bench_2mw)", 2, 1)
                preproce_middleware("2017-11-13_18h55(bench_2mw)", 2, 1)

                sys.exit(0)
            elif arg == "./preprocess.py":
                continue
            elif re.match(r"name=[\w()-]+", arg):
                experiment_name = re.match(r"name=[\w()-]+", arg).string.split("=")[1]
            elif re.match(r"clients=\d+", arg):
                clients = re.match(r"clients=\d+", arg).string.split("=")[1]
            elif re.match(r"mws=\d+", arg):
                mws = re.match(r"mws=\d+", arg).string.split("=")[1]
            elif re.match(r"tc=\d+", arg):
                tc = re.match(r"tc=\d+", arg).string.split("=")[1]
            else:
                print("Usage:\n\tpreprocess.py name=\"<name>\" clients=<client_count> mws=<mw_count> tc=<thread_count>")
                sys.exit(1)
        if experiment_name is None or clients is None or mws is None or tc is None:
            print("Usage:\n\tpreprocess.py name=\"<name>\" clients=<client_count> mws=<mw_count> tc=<thread_count>")
            sys.exit(1)

        if int(mws) == 0:
            preprosses_memtier(experiment_name, int(clients), int(tc))
        else:
            preprosses_memtier(experiment_name, int(clients), int(tc))
            preproce_middleware(experiment_name, int(mws), int(tc))

    else:
        print("Usage:\n\tpreprocess.py name=\"<name>\" clients=<client_count> mws=<mw_count> tc=<thread_count>")
        sys.exit(1)
