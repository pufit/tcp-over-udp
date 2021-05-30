FROM python:latest

RUN apt update && \
 DEBIAN_FRONTEND=noninteractive \
 apt-get install -y --allow-downgrades --allow-remove-essential --allow-change-held-packages \
 python3-pip

ADD docker/server/server.py /server/
ADD server /server/tcp_over_udp/server
ADD common /server/tcp_over_udp/common
ADD requirements.txt /server/

WORKDIR /server/

RUN python3 -m pip install -r /server/requirements.txt
