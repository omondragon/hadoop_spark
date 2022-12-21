#!/bin/bash

echo "Updating Ubuntu"
sudo apt-get update

echo "Installing jdk"
sudo apt-get install openjdk-8-jdk -y

echo "Adding hadoop user"
sudo adduser hadoop --gecos "First Last,RoomNumber,WorkPhone,HomePhone" --disabled-password
echo "hadoop:hadoop" | sudo chpasswd

echo "Download Hadoop"
su -l hadoop -c "wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz > .null;
tar -xzf hadoop-3.3.4.tar.gz > .null;
mv hadoop-3.3.4 hadoop"

echo "Install Spark"
su -l hadoop -c "wget https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz
tar -xvf spark-3.3.1-bin-hadoop3.tgz
mv spark-3.3.1-bin-hadoop3 spark"

echo "Set Environment Variables"
echo "export HADOOP_HOME=/home/hadoop/hadoop
export HADOOP_MAPRED_HOME=\$HADOOP_HOME
export HADOOP_COMMON_HOME=\$HADOOP_HOME
export HADOOP_HDFS_HOME=\$HADOOP_HOME
export YARN_HOME=\$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=\$HADOOP_HOME/lib/native
export PATH=$PATH:$HADOOP_HOME/sbin:\$HADOOP_HOME/bin
export LD_LIBRARY_PATH=/home/hadoop/hadoop/lib/native/:\$LD_LIBRARY_PATH
export HADOOP_INSTALL=\$HADOOP_HOME
export HADOOP_CONF_DIR=/home/hadoop/hadoop/etc/hadoop
PATH=/home/hadoop/spark/bin:$PATH
export SPARK_HOME=/home/hadoop/spark
export LD_LIBRARY_PATH=/home/hadoop/hadoop/lib/native:$LD_LIBRARY_PATH
JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre
PATH=/home/hadoop/hadoop/bin:/home/hadoop/hadoop/sbin:\$PATH" >> /home/hadoop/.bashrc
	source /home/hadoop/.bashrc
	sed -i "s/# export JAVA_HOME=.*/export JAVA_HOME=\/usr\/lib\/jvm\/java-8-openjdk-amd64\/jre/" /home/hadoop/hadoop/etc/hadoop/hadoop-env.sh

echo "Copying Configuration Files"
cp -r /vagrant/config/hadoop/* /home/hadoop/hadoop/etc/hadoop/

echo "Copy Config Spark Files"
cp /vagrant/config/spark/* /home/hadoop/spark/conf/
