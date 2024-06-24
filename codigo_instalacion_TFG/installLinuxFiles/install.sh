#!/bin/bash
apt-get update
apt-get install -y wget bzip2  make gcc libxslt1-dev libxml2-dev zlib1g-dev python3-pip git
mkdir  /compiler 
cd /compiler   || exit 1
wget -q -O - https://github.com/ttsiodras/asn1scc/releases/download/4.2.4.7f/asn1scc-bin-4.2.4.7f.tar.bz2 | tar jxvf -
apt-get -y install python3-pip
apt-get install libffi-dev
pip3 install --upgrade pip
pip3 install -r ../requirements.txt
pip install cassandra-driver
pip install cassandra-csv

# if ubuntu is version 22.04 openssl give problems ->  install libssl1.1
#apt-get install -y wget
# download package with wget
#wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb # quit comment if a problem with version openssl
# install package locally
#dpkg -i libssl1.1_1.1.0g-2ubuntu4_amd64.deb # quit comment if a problem with version openssl


