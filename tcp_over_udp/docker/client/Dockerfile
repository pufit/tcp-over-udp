FROM python:latest

RUN apt update && \
 DEBIAN_FRONTEND=noninteractive \
 apt-get install -y --allow-downgrades --allow-remove-essential --allow-change-held-packages \
 python3-pip


ADD docker/client/client.py /client/
ADD docker/client/files /client/files

ADD client /client/tcp_over_udp/client
ADD common /client/tcp_over_udp/common
ADD requirements.txt /client/

WORKDIR /client/

RUN python3 -m pip install -r /client/requirements.txt
