#!/usr/bin/env python3

import sys
import os
import pandas as pd
import csv

def aggregate_memtier(basedir, client_num):
    for operation in ["read", "write"]:
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            cwd = "{}/{}/{}_clients".format(basedir, operation, nclients)
            os.makedirs("processed/{}".format(cwd))
            with open("processed/{}/clients.csv".format(cwd), 'w', newline="") as outputfile:
                writer = csv.writer(outputfile)
                writer.writerow(["Client host",
                                 "Average Throughput",
                                 "Std Throughput",
                                 "Average Response Time",
                                 "Std Response Time"])
                cross_client_throughputs = pd.DataFrame([])
                cross_client_resp_time = pd.DataFrame([])
                for client in range(1, client_num + 1):
                    all_throughput = pd.DataFrame([])
                    all_resp_time = pd.DataFrame([])
                    # Gather data from all reps
                    for rep in [1, 2, 3]:
                        data = pd.read_csv("preprocessed/{}/client{}/rep{}.csv".format(cwd,
                                                                                       client,
                                                                                       rep),
                                           header=0)
                        all_throughput = pd.concat(([all_throughput, data["Throughput"]]))
                        all_resp_time = pd.concat(([all_resp_time, data["Latency"]]))

                    cross_client_resp_time = pd.concat([cross_client_resp_time, all_resp_time])

                    # Get total throughput
                    if cross_client_throughputs.empty:
                        cross_client_throughputs = all_throughput
                    else:
                        cross_client_throughputs += all_throughput

                    writer.writerow([client,
                                     float(all_throughput.mean()),
                                     float(all_throughput.std()),
                                     float(all_resp_time.mean()),
                                     float(all_resp_time.std())])

                writer.writerow(["Total",
                                 float(cross_client_throughputs.mean()),
                                 float(cross_client_throughputs.std()),
                                 float(cross_client_resp_time.mean()),
                                 float(cross_client_resp_time.std())])
            outputfile.close()

def aggregate_mw(basedir, client_num, mw_num):
    for operation in ["read", "write"]:
        for nworkers in [8, 16, 32, 64]:
            for nclients in [2, 4, 8, 14, 20, 26, 32]:
                cwd = "{}/{}/{}_workers/{}_clients".format(basedir, operation, nworkers, nclients)
                os.makedirs("processed/{}".format(cwd))
                with open("processed/{}/clients.csv".format(cwd), 'w', newline="") as outputfile:
                    writer = csv.writer(outputfile)
                    writer.writerow(["Client host",
                                     "Average Throughput",
                                     "Std Throughput",
                                     "Average Response Time",
                                     "Std Response Time"])
                    cross_client_throughputs = pd.DataFrame([])
                    cross_client_resp_time = pd.DataFrame([])
                    for client in range(1, client_num + 1):
                        all_throughput = pd.DataFrame([])
                        all_resp_time = pd.DataFrame([])
                        # Gather data from all reps
                        for rep in [1, 2, 3]:
                            data = pd.read_csv("preprocessed/{}/client{}/rep{}.csv".format(cwd,
                                                                                           client,
                                                                                           rep),
                                               header=0)
                            all_throughput = pd.concat(([all_throughput, data["Throughput"]]))
                            all_resp_time = pd.concat(([all_resp_time, data["Latency"]]))

                        cross_client_resp_time = pd.concat([cross_client_resp_time, all_resp_time])

                        # Get total throughput
                        if cross_client_throughputs.empty:
                            cross_client_throughputs = all_throughput
                        else:
                            cross_client_throughputs += all_throughput

                        writer.writerow([client,
                                         float(all_throughput.mean()),
                                         float(all_throughput.std()),
                                         float(all_resp_time.mean()),
                                         float(all_resp_time.std())])

                    writer.writerow(["Total",
                                     float(cross_client_throughputs.mean()),
                                     float(cross_client_throughputs.std()),
                                     float(cross_client_resp_time.mean()),
                                     float(cross_client_resp_time.std())])
                outputfile.close()

                with open("processed/{}/mws.csv".format(cwd), 'w', newline="") as outputfile:
                    writer = csv.writer(outputfile)
                    writer.writerow(["MW host",
                                     "Average Throughput",
                                     "Std Throughput",
                                     "Average Response Time",
                                     "Std Response Time",
                                     "Average Queue Time",
                                     "Std Queue Time",
                                     "Average Queue Length",
                                     "Std Queue Length",
                                     "Average Server Time",
                                     "Std Server Time"])
                    cross_mw_throughputs = pd.DataFrame([])
                    cross_mw_resp_time = pd.DataFrame([])
                    cross_mw_q_time = pd.DataFrame([])
                    cross_mw_q_len = pd.DataFrame([])
                    cross_mw_server_time = pd.DataFrame([])
                    for mw in range(1, mw_num + 1):
                        all_throughput = pd.DataFrame([])
                        all_resp_time = pd.DataFrame([])
                        all_q_time = pd.DataFrame([])
                        all_q_len = pd.DataFrame([])
                        all_server_time = pd.DataFrame([])
                        # Gather data from all reps
                        for rep in [1, 2, 3]:
                            data = pd.read_csv("preprocessed/{}/mw{}/rep{}.csv".format(cwd,
                                                                                       mw,
                                                                                       rep),
                                               header=0)
                            all_throughput = pd.concat(([all_throughput, data["TOT"]]))
                            all_resp_time = pd.concat(([all_resp_time, data["RSP T"]]))
                            all_q_time = pd.concat(([all_q_time, data["Q T"]]))
                            all_q_len = pd.concat(([all_q_len, data["Q LEN"]]))
                            all_server_time = pd.concat(([all_server_time, data["SVR T"]]))

                        cross_mw_resp_time = pd.concat([cross_mw_resp_time, all_resp_time])
                        cross_mw_q_time = pd.concat([cross_mw_q_time, all_q_time])
                        cross_mw_server_time = pd.concat([cross_mw_server_time, all_server_time])

                        # Get total throughput
                        if cross_mw_throughputs.empty:
                            cross_mw_throughputs = all_throughput
                        else:
                            cross_mw_throughputs += all_throughput

                        # Get total queue length
                        if cross_mw_q_len.empty:
                            cross_mw_q_len = all_q_len
                        else:
                            cross_mw_q_len += all_q_len

                        # Convert all timing into milli-seconds
                        all_resp_time /= 1000
                        all_q_time /= 1000
                        all_server_time /= 1000

                        writer.writerow([mw,
                                         float(all_throughput.mean()),
                                         float(all_throughput.std()),
                                         float(all_resp_time.mean()),
                                         float(all_resp_time.std()),
                                         float(all_q_time.mean()),
                                         float(all_q_time.std()),
                                         float(all_q_len.mean()),
                                         float(all_q_len.std()),
                                         float(all_server_time.mean()),
                                         float(all_server_time.std())])

                    # Convert all timing into milli-seconds
                    cross_mw_resp_time /= 1000
                    cross_mw_q_time /= 1000
                    cross_mw_server_time /= 1000

                    writer.writerow(["Total",
                                     float(cross_mw_throughputs.mean()),
                                     float(cross_mw_throughputs.std()),
                                     float(cross_mw_resp_time.mean()),
                                     float(cross_mw_resp_time.std()),
                                     float(cross_mw_q_time.mean()),
                                     float(cross_mw_q_time.std()),
                                     float(cross_mw_q_len.mean()),
                                     float(cross_mw_q_len.std()),
                                     float(cross_mw_server_time.mean()),
                                     float(cross_mw_server_time.std())])
                outputfile.close()


if __name__ == "__main__":
    if sys.argv[1] == "all":
        aggregate_memtier("bench_clients", 2)
        aggregate_memtier("bench_memcached", 3)
        aggregate_mw("bench_1mw", 1, 1)
        aggregate_mw("bench_2mw", 2, 2)
