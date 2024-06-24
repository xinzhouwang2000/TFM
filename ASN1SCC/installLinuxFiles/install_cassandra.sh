#!/bin/bash
apt-get update
apt install curl -y
apt install default-jdk -y
apt-get install -y gnupg2 gnupg gnupg1
echo "deb https://debian.cassandra.apache.org 41x main" |  tee -a /etc/apt/sources.list.d/cassandra.sources.list
curl https://downloads.apache.org/cassandra/KEYS |  apt-key add -
apt-get update
apt-get install cassandra -y
service cassandra start

     