#!/usr/bin/env python3

import os
import sys
import csv
import statistics


def memtier_throughtput(basedir):
    """Docstring"""

    with open("final/{}.csv".format(basedir), 'w') as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(["Operation", "Clients", "Throughput", "Latency(ms)"])
        for operation in ["read", "write"]:
            for nclients in [1, 2, 4, 8, 16, 24, 32]:
                with open("processed/{}/{}/{}_clients.csv".format(basedir, operation, nclients), 'r') as inputfile:
                    reader = csv.reader(inputfile)
                    # Skip headers
                    next(reader, None)
                    # Compute averages
                    data = [row for row in reader]
                    mean_throughput = statistics.mean(int(record[0]) for record in data)
                    mean_latency = statistics.mean(float(record[1]) for record in data)

                    writer.writerow([operation, nclients, mean_throughput, mean_latency])
                inputfile.close()
    outputfile.close()

if __name__ == "__main__":
    if sys.argv[1] == "all":
        memtier_throughtput("bench_clients")
        memtier_throughtput("bench_memcached")
    else:
        memtier_throughtput(sys.argv[1])
