#!/usr/bin/env python3

import sys
import os
import csv

def aggregate(name):
    """Aggregates the data from preprocessed dstat data.
    Arguments:
        name: string of the experiment name"""
    inputfilename = os.path.join("processed",
                                 name,
                                 "dstat.csv")
    outputfilename = os.path.join("final",
                                  name,
                                  "dstat.csv")
    with open(inputfilename, 'r', newline="") as inputfile:
        with open(outputfilename, 'w', newline="") as outputfile:
            reader = csv.reader(inputfile)
            writer = csv.writer(outputfile)
            writer.writerow(["Operation",
                             "Sharded",
                             "Workers",
                             "Clients",
                             "Machine type",
                             "Average CPU usage",
                             "Std CPU usage",
                             "Average Network receive",
                             "Std Network receive",
                             "Average Network write",
                             "Std Network write"])

            for row in reader:
                if row[5] == "total":
                    writer.writerow(row[:5] + row[6:])
        outputfile.close()
    inputfile.close()


if __name__ == "__main__":
    if sys.argv[1] == "all":
        aggregate("benchmark_memcached")
        aggregate("benchmark_clients")
        aggregate("benchmark_1mw")
        aggregate("benchmark_2mw")
        aggregate("throughput_writes")
        aggregate("get_and_multigets")
