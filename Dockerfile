FROM ubuntu:24.04

# Setup python and java and base system
ENV DEBIAN_FRONTEND noninteractive
ENV LANG=en_US.UTF-8

RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get install -q -y openjdk-8-jdk python3-pip wget unzip maven inotify-tools

# Install MetaMapLite
RUN mkdir /opt/metamaplite
RUN mkdir /opt/metamaplite/data
RUN mkdir /opt/metamaplite/public_mm_lite
RUN mkdir /opt/metamaplite/inbox
RUN mkdir /opt/metamaplite/outbox
RUN mkdir /opt/metamaplite/error

RUN cd /opt/metamaplite
RUN wget https://github.com/LHNCBC/metamaplite/archive/refs/tags/RELEASE3.6.2rc8.zip
RUN unzip RELEASE3.6.2rc8.zip
RUN rm RELEASE3.6.2rc8.zip
RUN mv metamaplite-RELEASE3.6.2rc8
RUN mvn clean install


# Install CDS

# Install PDS

# Install nginx webserver to view pipeline
RUN sudo apt install nginx \
    && sudo systemctl enable nginx \
    && sudo systemctl start nginx



