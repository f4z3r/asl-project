#!/usr/bin/env python3

import sys
import os
import csv
import statistics


def memtier_throughtput(basedir):
    """Docstring"""
    os.mkdir("final/{}/".format(basedir))
    with open("final/{}/{}.csv".format(basedir, basedir), 'w') as outputfile:
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
                    mean_throughput = statistics.mean(float(record[0]) for record in data)
                    mean_latency = statistics.mean(float(record[1]) for record in data)

                    writer.writerow([operation, nclients, mean_throughput, mean_latency])
                inputfile.close()
    outputfile.close()

def mw_throughtput(basedir):
    """Docstring"""
    os.mkdir("final/{}/".format(basedir))
    with open("final/{}/{}_memtier.csv".format(basedir, basedir), 'w') as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(["Operation", "Workers", "Clients", "Throughput", "Latency(ms)"])
        for operation in ["read", "write"]:
            for workers in [8, 16, 32, 64]:
                for nclients in [2, 4, 8, 14, 20, 26, 32]:
                    with open("processed/{}/{}/{}_workers/{}_clients.csv".format(basedir, operation, workers, nclients), 'r') as inputfile:
                        reader = csv.reader(inputfile)
                        # Skip headers
                        next(reader, None)
                        # Compute averages
                        data = [row for row in reader]
                        mean_throughput = statistics.mean(float(record[0]) for record in data)
                        mean_latency = statistics.mean(float(record[1]) for record in data)

                        writer.writerow([operation, workers, nclients, mean_throughput, mean_latency])
                    inputfile.close()
    outputfile.close()

    with open("final/{}/{}_mw.csv".format(basedir, basedir), 'w') as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(["Operation", "Workers", "Clients", "Throughput", "Reponse time(ms)", "Queue time(ms)", "Queue length"])
        for operation in ["read", "write"]:
            for workers in [8, 16, 32, 64]:
                for nclients in [2, 4, 8, 14, 20, 26, 32]:
                    with open("processed/{}/{}/{}_workers/mws_{}clients.csv".format(basedir, operation, workers, nclients), 'r') as inputfile:
                        reader = csv.reader(inputfile)
                        # Skip headers
                        next(reader, None)
                        # Compute averages
                        data = [row for row in reader]
                        mean_throughput = statistics.mean(float(record[0]) for record in data)
                        mean_resp_t = statistics.mean(float(record[1]) for record in data) / 1000
                        mean_q_t = statistics.mean(float(record[2]) for record in data) / 1000
                        mean_q_len = statistics.mean(float(record[3]) for record in data)

                        writer.writerow([operation, workers, nclients, mean_throughput, mean_resp_t, mean_q_t, mean_q_len])
                    inputfile.close()
    outputfile.close()

if __name__ == "__main__":
    if sys.argv[1] == "all":
        memtier_throughtput("bench_clients")
        memtier_throughtput("bench_memcached")
        mw_throughtput("bench_1mw")
        mw_throughtput("bench_2mw")
    else:
        memtier_throughtput(sys.argv[1])
