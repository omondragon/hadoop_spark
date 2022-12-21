#!/bin/bash
time spark-submit --master yarn --deploy-mode cluster --executor-memory 512m --driver-memory 512m --num-executors 2 --executor-cores 1 ji_py3.py
