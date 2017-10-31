#! /bin/bash

sleepcmd="sleep $1"
$sleepcmd

PID=$(ps ax | grep RunMW | grep -v grep | head -n1 | cut -c-5)
killcmd="kill -SIGINT ${PID}"
$killcmd
