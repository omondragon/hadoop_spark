#!/bin/bash


echo "Updating Ubuntu"
sudo apt-get update

echo "Installing jdk"
sudo apt-get install openjdk-8-jdk -y

echo "Adding hadoop user"
sudo adduser hadoop --gecos "First Last,RoomNumber,WorkPhone,HomePhone" --disabled-password
echo "hadoop:hadoop" | sudo chpasswd

echo "Copying SSH Keys"
sudo apt-get install sshpass -y
sshpass -p 'hadoop' ssh -o StrictHostKeyChecking=no hadoop@nodemaster 'ssh-keygen -b 4096 -N "" -f /home/hadoop/.ssh/id_rsa'
sshpass -p 'hadoop' ssh-copy-id -o StrictHostKeyChecking=no -i /home/hadoop/.ssh/id_rsa.pub hadoop@nodemaster
sshpass -p 'hadoop' ssh-copy-id -o StrictHostKeyChecking=no -i /home/hadoop/.ssh/id_rsa.pub hadoop@node1
sshpass -p 'hadoop' ssh-copy-id -o StrictHostKeyChecking=no -i /home/hadoop/.ssh/id_rsa.pub hadoop@node2

echo "Download Hadoop"
su -l hadoop -c "wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.4/hadoop-3.3.4.tar.gz > .null;
tar -xzf hadoop-3.3.4.tar.gz > .null;
mv hadoop-3.3.4 hadoop"

echo "Install Spark"
su -l hadoop -c "wget https://dlcdn.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz
tar -xvf spark-3.3.2-bin-hadoop3.tgz
mv spark-3.3.2-bin-hadoop3 spark"

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

#Install libraries
sudo apt-get install zip -y

echo "Starting Hadoop and HDFS"
sudo -H -u hadoop bash -c  "/home/hadoop/hadoop/bin/hdfs namenode -format"
sudo -H -u hadoop bash -c  "/home/hadoop/hadoop/sbin/start-dfs.sh"
sudo -H -u hadoop bash -c  "/home/hadoop/hadoop/sbin/start-yarn.sh"

echo "Creating needed directories in HDFS"
sudo -H -u hadoop bash -c  "/home/hadoop/hadoop/bin/hdfs dfs -mkdir -p /user/hadoop"
sudo -H -u hadoop bash -c  "/home/hadoop/hadoop/bin/hdfs dfs -mkdir /spark-logs"
sudo -H -u hadoop bash -c  "/home/hadoop/hadoop/bin/hdfs dfs -mkdir vids"

echo "Setting permissions to run_traffic.sh"
sudo -H -u hadoop bash -c "chmod 755 /vagrant/src/run_traffic.sh"
