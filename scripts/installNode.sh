#!/bin/bash
# -*- ENCODING: UTF-8 -*-
# Worker node script

# Update ubuntu
echo "Updating Ubuntu"
sudo apt-get update

echo "Installing OpenCV"
sudo apt install python3-pip -y
sudo apt install python3-opencv libopencv-dev -y
sudo pip install opencv-python
sudo pip install opencv-contrib-python

echo "Installing hdfs and pyspark libraries"
sudo pip install hdfs
sudo pip install pyspark

echo "Installing numpy"
sudo pip install numpy

