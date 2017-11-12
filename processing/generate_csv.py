#!/usr/bin/env python3

import os
import sys
import re
import csv

def handle_memtier(basedir):
    """Creates a csv file containing throughput, response time for every second."""

    os.mkdir("processed/{}".format(basedir))
    for operation in ["read", "write"]:
        os.mkdir("processed/{}/{}".format(basedir, operation))
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            with open("processed/{}/{}/{}_clients.csv".format(basedir, operation, nclients), 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(["Throughput", "latency(ms)"])
                for rep in [1, 2, 3]:
                    with open("preprocessed/{}/{}/{}_clients/rep{}.log".format(basedir, operation, nclients, rep), 'r') as inputfile:
                        for line in inputfile.readlines():
                            contents = re.split("\s", line)
                            contents = list(filter(None, contents))
                            writer.writerow([contents[9], contents[16]])
                    inputfile.close()
            csvfile.close()


if __name__ == "__main__":
    if sys.argv[1] == "all":
        handle_memtier("bench_clients")
        handle_memtier("bench_memcached")
    else:
        handle_memtier(sys.argv[1])
