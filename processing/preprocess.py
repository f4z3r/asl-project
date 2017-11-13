#!/usr/bin/env python3

import os
import sys
import re

valid_line = re.compile(r"\[RUN #1\s+\d+%,\s+\d+ secs\]")
last_line = re.compile(r"\[RUN #1\s+100%,\s+90 secs\]")

def bench_memcached():
    """Docstring"""

    experiment_name = "2017-11-11_17h12(bench_memcached)"

    os.mkdir("preprocessed/bench_memcached")
    for operation in ["read", "write"]:
        os.mkdir("preprocessed/bench_memcached/{}".format(operation))
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            cwd = "preprocessed/bench_memcached/{}/{}_clients".format(operation, nclients)
            os.mkdir(cwd)
            for client in range(1, 4):
                os.mkdir("{}/client{}".format(cwd, client))
                for rep in range(1, 4):
                    with open("{}/client{}/rep{}.log".format(cwd, client, rep), 'w') as writefile:
                        with open("../logs/{}/2threads".format(experiment_name) +\
                                "_{}clients_{}/clients/client{}_{}.log".format(nclients, operation, client, rep), 'r') as readfile:
                            # Skip the first two lines of input file
                            for content in readfile.readlines():
                                content.strip()
                                if re.match(valid_line, content):
                                    # lines = re.split(valid_line, content)
                                    lines = content.split("\r")
                                    for line in lines:
                                        line.strip()
                                        if not re.match(last_line, line):
                                            print(line, file=writefile, end="")
                        readfile.close()
                    writefile.close()

def bench_clients():
    """Docstring"""

    experiment_name = "2017-11-11_18h21(bench_clients)"

    os.mkdir("preprocessed/bench_clients")
    for operation in ["read", "write"]:
        os.mkdir("preprocessed/bench_clients/{}".format(operation))
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            cwd = "preprocessed/bench_clients/{}/{}_clients".format(operation, nclients)
            os.mkdir(cwd)
            for client in range(1, 3):
                os.mkdir("{}/client{}".format(cwd, client))
                for rep in range(1, 4):
                    with open("{}/client{}/rep{}.log".format(cwd, client, rep), 'w') as writefile:
                        with open("../logs/{}/1threads".format(experiment_name) +\
                                "_{}clients_{}/clients/client1-{}_{}.log".format(nclients, operation, client, rep), 'r') as readfile:
                            # Skip the first two lines of input file
                            for content in readfile.readlines():
                                content.strip()
                                if re.match(valid_line, content):
                                    # lines = re.split(valid_line, content)
                                    lines = content.split("\r")
                                    for line in lines:
                                        line.strip()
                                        if not re.match(last_line, line):
                                            print(line, file=writefile, end="")
                        readfile.close()
                    writefile.close()


def bench_1mw():
    """Docstring"""

    experiment_name = "2017-11-12_16h58(benchmark_1mw)"

    os.mkdir("preprocessed/bench_1mw")
    for operation in ["read", "write"]:
        os.mkdir("preprocessed/bench_1mw/{}".format(operation))
        for nworkers in [8, 16, 32, 64]:
            os.mkdir("preprocessed/bench_1mw/{}/{}_workers".format(operation, nworkers))
            for nclients in [2, 4, 8, 14, 20, 26, 32]:
                cwd = "preprocessed/bench_1mw/{}/{}_workers/{}_clients".format(operation, nworkers, nclients)
                os.mkdir(cwd)
                for rep in range(1, 4):
                    with open("{}/client_rep{}.log".format(cwd, rep), 'w') as writefile:
                        with open("../logs/{}/{}_workers/2threads".format(experiment_name, nworkers) +\
                                "_{}clients_{}/clients/client1_{}.log".format(nclients, operation, rep), 'r') as readfile:
                            # Skip the first two lines of input file
                            for content in readfile.readlines():
                                content.strip()
                                if re.match(valid_line, content):
                                    # lines = re.split(valid_line, content)
                                    lines = content.split("\r")
                                    for line in lines:
                                        line.strip()
                                        if not re.match(last_line, line):
                                            print(line, file=writefile, end="")
                        readfile.close()
                    writefile.close()
                    with open("{}/mw_rep{}.log".format(cwd, rep), 'w') as writefile:
                        with open("../logs/{}/{}_workers/2threads".format(experiment_name, nworkers) +\
                                "_{}clients_{}/mw/mw1_{}.log".format(nclients, operation, rep), 'r') as readfile:
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


def bench_2mw():
    """Docstring"""

    experiment_name = "2017-11-12_23h02(benchmark_2mw)"

    os.mkdir("preprocessed/bench_2mw")
    for operation in ["read", "write"]:
        os.mkdir("preprocessed/bench_2mw/{}".format(operation))
        for nworkers in [8, 16, 32, 64]:
            os.mkdir("preprocessed/bench_2mw/{}/{}_workers".format(operation, nworkers))
            for nclients in [2, 4, 8, 14, 20, 26, 32]:
                cwd = "preprocessed/bench_2mw/{}/{}_workers/{}_clients".format(operation, nworkers, nclients)
                os.mkdir(cwd)
                for machine in range(1, 3):
                    for rep in range(1, 4):
                        with open("{}/client{}_rep{}.log".format(cwd, machine, rep), 'w') as writefile:
                            with open("../logs/{}/{}_workers/1threads".format(experiment_name, nworkers) +\
                                    "_{}clients_{}/clients/client1-{}_{}.log".format(nclients, operation, machine, rep), 'r') as readfile:
                                # Skip the first two lines of input file
                                for content in readfile.readlines():
                                    content.strip()
                                    if re.match(valid_line, content):
                                        # lines = re.split(valid_line, content)
                                        lines = content.split("\r")
                                        for line in lines:
                                            line.strip()
                                            if not re.match(last_line, line):
                                                print(line, file=writefile, end="")
                            readfile.close()
                        writefile.close()
                        with open("{}/mw{}_rep{}.log".format(cwd, machine, rep), 'w') as writefile:
                            with open("../logs/{}/{}_workers/1threads".format(experiment_name, nworkers) +\
                                    "_{}clients_{}/mw/mw{}_{}.log".format(nclients, operation, machine, rep), 'r') as readfile:
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
    if sys.argv[1] == "bench_memcached":
        bench_memcached()
    if sys.argv[1] == "bench_clients":
        bench_clients()
    if sys.argv[1] == "bench_1mw":
        bench_1mw()
    if sys.argv[1] == "bench_2mw":
        bench_2mw()
    if sys.argv[1] == "all":
        bench_memcached()
        bench_clients()
