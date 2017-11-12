#!/usr/bin/env python3

import os
import sys
import re
import csv

def handle_memtier(basedir):
    """Creates a csv file containing throughput, response time """"
    for operation in ["read", "write"]:
        for nclients in [1, 2, 4, 8, 16, 24, 32]:
            with open("preprocessed/" + basedir + "/{}clients_{}.log".format(nclients, operation), 'r') as inputfile:
                
