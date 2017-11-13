#!/usr/bin/env python3

import os
import sys
import re
import csv
import numpy as np

def memtier_clients():
    """Creates a csv file containing combined throughput, response time for every second."""
    basedir = "bench_clients"
    os.mkdir("processed/{}".format(basedir))
    for operation in ["read", "write"]:
        os.mkdir("processed/{}/{}".format(basedir, operation))
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            with open("processed/{}/{}/{}_clients.csv".format(basedir, operation, nclients), 'w') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Throughput", "latency(ms)"])

                data = np.zeros(shape=(89, 2))

                for client in [1, 2]:
                    averages = np.zeros(shape=(89, 2))

                    for rep in [1, 2, 3]:
                        with open("preprocessed/{}/{}/{}_clients/client{}/rep{}.log".format(basedir, operation, nclients, client, rep), 'r') as inputfile:
                            content = []
                            for line in inputfile.readlines():
                                line_content = re.split(r"\s", line)
                                line_content = list(filter(None, line_content))
                                content += [[int(line_content[9]), float(line_content[16])]]

                            content_matrix = np.matrix(content)
                            averages += content_matrix
                        inputfile.close()

                    averages /= 3
                    data += averages

                for row in data:
                    # Get average response time
                    row[1] /= 2
                    writer.writerow(row)

            csvfile.close()

def memtier_memcached():
    """Creates a csv file containing combined throughput, response time for every second."""
    basedir = "bench_memcached"
    os.mkdir("processed/{}".format(basedir))
    for operation in ["read", "write"]:
        os.mkdir("processed/{}/{}".format(basedir, operation))
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            with open("processed/{}/{}/{}_clients.csv".format(basedir, operation, nclients), 'w') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Throughput", "latency(ms)"])

                data = np.zeros(shape=(89, 2))

                for client in [1, 2, 3]:
                    averages = np.zeros(shape=(89, 2))

                    for rep in [1, 2, 3]:
                        with open("preprocessed/{}/{}/{}_clients/client{}/rep{}.log".format(basedir, operation, nclients, client, rep), 'r') as inputfile:
                            content = []
                            for line in inputfile.readlines():
                                line_content = re.split(r"\s", line)
                                line_content = list(filter(None, line_content))
                                content += [[int(line_content[9]), float(line_content[16])]]

                            content_matrix = np.matrix(content)
                            averages += content_matrix
                        inputfile.close()

                    averages /= 3
                    data += averages

                for row in data:
                    # Get average response time
                    row[1] /= 3
                    writer.writerow(row)

            csvfile.close()


if __name__ == "__main__":
    if sys.argv[1] == "all":
        memtier_clients()
        memtier_memcached()
    if sys.argv[1] == "bench_clients":
        memtier_clients()
    if sys.argv[1] == "bench_memcached":
        memtier_memcached()
