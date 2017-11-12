#!/usr/bin/env python3

import os
import sys
import re
import matplotlib as mpl

def bench_memcached():
    valid_line = re.compile("\[RUN #1\s+\d+%,\s+\d+ secs\]")

    os.mkdir("preprocessed/bench_memcached")
    for operation in ["read", "write"]:
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            with open("preprocessed/bench_memcached/{}clients_{}.log".format(nclients, operation), 'w') as writefile:
                for client in range(1, 4):
                    for rep in range(1, 4):
                        with open("../logs/2017-11-11_17h12(bench_memcached)/2threads" +\
                                "_{}clients_{}/clients/client{}_{}.log".format(nclients, operation, client, rep), 'r') as readfile:
                            # Skip the first two lines of input file
                            for content in readfile.readlines():
                                content.strip()
                                if re.match(valid_line, content):
                                    # lines = re.split(valid_line, content)
                                    lines = content.split("\r")
                                    for line in lines:
                                        line.strip()
                                        print(line, file=writefile, end="")
                        readfile.close()
            writefile.close()

def bench_clients():
    valid_line = re.compile("\[RUN #1\s+\d+%,\s+\d+ secs\]")

    os.mkdir("preprocessed/bench_clients")
    for operation in ["read", "write"]:
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            with open("preprocessed/bench_clients/{}clients_{}.log".format(nclients, operation), 'w') as writefile:
                for client in range(1, 3):
                    for rep in range(1, 4):
                        with open("../logs/2017-11-11_18h21(bench_clients)/1threads" +\
                                "_{}clients_{}/clients/client1-{}_{}.log".format(nclients, operation, client, rep), 'r') as readfile:
                            # Skip the first two lines of input file
                            for content in readfile.readlines():
                                content.strip()
                                if re.match(valid_line, content):
                                    # lines = re.split(valid_line, content)
                                    lines = content.split("\r")
                                    for line in lines:
                                        line.strip()
                                        print(line, file=writefile, end="")
                        readfile.close()
            writefile.close()

if __name__ == "__main__":
    if sys.argv[1] == "bench_memcached":
        bench_memcached()
    if sys.argv[1] == "bench_clients":
        bench_clients()
