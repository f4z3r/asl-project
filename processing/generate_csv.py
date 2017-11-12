#!/usr/bin/env python3

import os
import sys
import re
import csv

def handle_memtier(basedir):
    for operation in ["read", "write"]:
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            with open("preprocessed/" + basedir + "/{}clients_{}.log".format(nclients, operation), 'r') as inputfile:
                with open("assets/" + basedir + "/{}clients_{}.csv".format(nclients, operation), 'w') as csvfile:
                    writer = csv.writer(csvfile, delimiter=", ")

                    for line in inputfile.readlines():
                        line.
