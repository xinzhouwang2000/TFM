FROM debian:buster

RUN apt-get update
RUN apt-get install -y wget bzip2 libicu63 make gcc libxslt1-dev libxml2-dev zlib1g-dev python3-pip git
RUN mkdir -p /usr/local/share/ 
RUN cd /usr/local/share/  || exit 1
RUN wget -q -O - https://github.com/ttsiodras/asn1scc/releases/download/4.2.4.7f/asn1scc-bin-4.2.4.7f.tar.bz2 | tar jxvf -
ENV PATH="/asn1scc:$PATH" 
RUN apt clean
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt
RUN apt install libffi-dev
RUN pip3 install --upgrade pip
RUN pip install cassandra-driver
RUN pip install cassandra-csv
