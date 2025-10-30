FROM ubuntu:24.04

# Setup python and java and base system
ENV DEBIAN_FRONTEND noninteractive
ENV LANG=en_US.UTF-8

RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get install -q -y openjdk-21-jdk python3-pip wget unzip maven inotify-tools nginx vim python3-numpy python3-matplotlib python3-watchdog

# build metamap lite
COPY ./metamap_install_files /opt/metamap_install_files
RUN cd /opt && \
    unzip /opt/metamap_install_files/public_mm_lite_3.6.2rc8_binaryonly.zip && \
    unzip /opt/metamap_install_files/public_mm_data_lite_usabase_2022aa.zip && \
    unzip /opt/metamap_install_files/public_mm_data_lite_usabase_2022ab.zip

# copy source code to docker
copy ./brat2csv /opt/brat2csv
COPY ./cds /opt/cds
COPY ./com /opt/com
COPY ./models /opt/models
COPY ./PDS /opt/PDS


WORKDIR /opt/com

#CMD ["python3", "file_watcher.py"]
