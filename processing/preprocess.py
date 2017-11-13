#!/usr/bin/env python3

import os
import sys
import re

valid_line = re.compile(r"\[RUN #1\s+\d+%,\s+\d+ secs\]")
last_line = re.compile(r"\[RUN #1\s+100%,\s+90 secs\]")

def preprosses_memtier(experiment_name, client_count, thread_count):
    """Docstring"""

    sub_clients = False
    if re.match(r"bench_memcached", experiment_name):
        experiment = "bench_memcached"
    elif re.match(r"bench_clients", experiment_name):
        experiment = "bench_clients"
        sub_clients = True
    elif re.match(r"bench_1mw", experiment_name):
        experiment = "bench_1mw"
    elif re.match(r"bench_2mw", experiment_name):
        experiment = "bench_2mw"

    for operation in ["read", "write"]:
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            cwd = "preprocessed/{}/{}/{}_clients".format(experiment, operation, nclients)
            for client in range(1, client_count + 1):
                os.makedirs("{}/client{}".format(cwd, client))
                for rep in range(1, 4):
                    with open("{}/client{}/rep{}.log".format(cwd, client, rep), 'w') as writefile:
                        if sub_clients:
                            filename = "../logs/{}/{}threads_{}clients_{}/clients/client1-{}_{}.log".format(experiment_name, thread_count, nclients, operation, client, rep)
                        else:
                            filename = "../logs/{}/{}threads_{}clients_{}/clients/client{}_{}.log".format(experiment_name, thread_count, nclients, operation, client, rep)
                        with open(filename, 'r') as readfile:
                            # Skip the first two lines of input file
                            line_num = 0
                            for content in readfile.readlines():
                                content.strip()
                                if re.match(valid_line, content):
                                    lines = content.split("\r")
                                    for line in lines:
                                        line.strip()
                                        if not re.match(last_line, line):
                                            line_num += 1
                                            if line_num < 89:
                                                print(line, file=writefile, end="")
                        readfile.close()
                    writefile.close()


def preproce_middleware(experiment_name, mw_count, thread_count):
    """Docstring"""

    if re.match(r"bench_1mw", experiment_name):
        experiment = "bench_1mw"
    elif re.match(r"bench_2mw", experiment_name):
        experiment = "bench_2mw"

    for operation in ["read", "write"]:
        for nworkers in [8, 16, 32, 64]:
            for nclients in [2, 4, 8, 14, 20, 26, 32]:
                for mw in range(1, mw_count + 1):
                    cwd = "preprocessed/{}/{}/{}_workers/{}_clients/mw{}".format(experiment, operation, nworkers, nclients, mw)
                    os.makedirs(cwd)
                    for rep in range(1, 4):
                        with open("{}/mw{}_rep{}.log".format(cwd, mid, rep), 'w') as writefile:
                            with open("../logs/{}/{}_workers/{}threads".format(experiment_name, nworkers, thread_count) +\
                                    "_{}clients_{}/mw/mw{}_{}.log".format(nclients, operation, mw, rep), 'r') as readfile:
                                # Skip headers and first row (warmup time)
                                for line in readfile.readlines():
                                    contents = re.split(r"\s", line)
                                    contents = list(filter(None, contents))
                                    if contents == []:
                                        continue
                                    if re.match(r"=+", line):
                                        break
                                    if not (re.match(r"\d+", contents[0].strip()) or re.match(r"SETS", contents[0])):
                                        continue
                                    print(line, file=writefile, end="")
                            readfile.close()
                        writefile.close()





if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == "./preprocess.py":
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
