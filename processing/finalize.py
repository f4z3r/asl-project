#!/usr/bin/env python3


import sys
import os
import csv


def bench_no_mw(basedir):
    try:
        os.mkdir("final/{}".format(basedir))
    except:
        pass
    with open("final/{}/data.csv".format(basedir), 'w', newline="") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(["Operation",
                         "Clients",
                         "Average Throughtput",
                         "Std Throughput",
                         "Average Response Time",
                         "Std Response Time"])
        for operation in ["read", "write"]:
            for nclients in [1, 2, 4, 8, 16, 24, 32]:
                cwd = "processed/{}/{}/{}_clients".format(basedir, operation, nclients)
                with open("{}/clients.csv".format(cwd), 'r', newline="") as inputfile:
                    reader = csv.reader(inputfile)
                    for row in reader:
                        if row[0] == "Total":
                            writer.writerow([operation, nclients] + row[1:])
                inputfile.close()
    outputfile.close()

def bench_mw(basedir):
    try:
        os.mkdir("final/{}".format(basedir))
    except:
        pass
    with open("final/{}/data.csv".format(basedir), 'w', newline="") as outputfile:
        writer = csv.writer(outputfile)
        writer.writerow(["Operation",
                         "Workers",
                         "Clients",
                         "Average Throughput (client)",
                         "Std Throughput (client)",
                         "Average Response Time (client)",
                         "Std Response Time (client)",
                         "Average Throughput (mw)",
                         "Std Throughput (mw)",
                         "Average Response Time (mw)",
                         "Std Response Time (mw)",
                         "Average Queue Time (mw)",
                         "Std Queue Time (mw)",
                         "Average Queue Length (mw)",
                         "Std Queue Length (mw)",
                         "Average Server Time (mw)",
                         "Std Server Time (mw)"])
        for operation in ["read", "write"]:
            for nworkers in [8, 16, 32, 64]:
                for nclients in [2, 4, 8, 14, 20, 26, 32]:
                    cwd = "processed/{}/{}/{}_workers/{}_clients".format(basedir,
                                                                         operation,
                                                                         nworkers,
                                                                         nclients)
                    with open("{}/clients.csv".format(cwd), 'r', newline="") as inputfile:
                        reader = csv.reader(inputfile)
                        for row in reader:
                            if row[0] == "Total":
                                client_data = row[1:]
                    inputfile.close()
                    with open("{}/mws.csv".format(cwd), 'r', newline="") as inputfile:
                        reader = csv.reader(inputfile)
                        for row in reader:
                            if row[0] == "Total":
                                mw_data = row[1:]
                    inputfile.close()
                    writer.writerow([operation, nworkers, nclients] + client_data + mw_data)
    outputfile.close()

if __name__ == "__main__":
    if sys.argv[1] == "all":
        bench_no_mw("bench_clients")
        bench_no_mw("bench_memcached")
        bench_mw("bench_1mw")
        bench_mw("bench_2mw")
