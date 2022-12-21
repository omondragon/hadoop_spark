#!/bin/bash
# -*- ENCODING: UTF-8 -*-
# Master node script

# Avoid interactive questions
export DEBIAN_FRONTEND=noninteractive


# Update ubuntu
echo "Updating Ubuntu"
sudo apt-get update

echo "Installing hdfs library"
sudo apt install python3-pip
sudo pip install hdfs
