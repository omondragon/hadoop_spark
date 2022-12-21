#!/bin/bash
# -*- ENCODING: UTF-8 -*-
# Master node script

# Update ubuntu
echo "Updating Ubuntu"
sudo apt-get update

echo "Installing hdfs library"
sudo apt install python3-pip -y
sudo pip install hdfs
