#!/usr/bin/env python3

import os
import sys
import re
import csv
import numpy as np

def handle_memtier(basedir, client_num):
    """Creates a csv file containing combined throughput, response time for every second."""
    os.mkdir("processed/{}".format(basedir))
    for operation in ["read", "write"]:
        os.mkdir("processed/{}/{}".format(basedir, operation))
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            with open("processed/{}/{}/{}_clients.csv".format(basedir, operation, nclients), 'w') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Throughput", "latency(ms)"])

                data = np.zeros(shape=(89, 2))

                for client in range(1, client_num + 1):
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
                    row[1] /= client_num
                    writer.writerow(row)

            csvfile.close()

def handle_middleware(basedir, mw_num):
    """Creates a csv file containing combined throughput, response time and queue length for every second."""
    os.mkdir("processed/{}".format(basedir))
    for operation in ["read", "write"]:
        os.mkdir("processed/{}/{}".format(basedir, operation))
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            with open("processed/{}/{}/mw.csv".format(basedir, operation, nclients), 'w') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Throughput", "latency(ms)", "Queue length"])

                data = np.zeros(shape=(82, 3))

                for client in range(1, mw_num + 1):
                    averages = np.zeros(shape=(82, 3))

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
                    row[1] /= client_num
                    writer.writerow(row)

            csvfile.close()


if __name__ == "__main__":
    if sys.argv[1] == "all":
        handle_memtier("bench_clients", 2)
        handle_memtier("bench_memcached", 3)
    if sys.argv[1] == "bench_clients":
        handle_memtier("bench_clients", 2)
    if sys.argv[1] == "bench_memcached":
        handle_memtier("bench_memcached", 3)
