#!/bin/bash

# Run on the cluster
time spark-submit --master yarn --deploy-mode cluster --executor-memory 512m --driver-memory 512m --num-executors 2 --executor-cores 1 conteoVehicular.py

# Run local (on a worker)
#time spark-submit --deploy-mode client --executor-memory 512m --driver-memory 512m --num-executors 1 --executor-cores 1 conteoVehicular.py
