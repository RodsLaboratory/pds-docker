FROM ubuntu:24.04

# Setup python and java and base system
ENV DEBIAN_FRONTEND noninteractive
ENV LANG=en_US.UTF-8

RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get install -q -y openjdk-21-jdk python3-pip wget unzip maven inotify-tools nginx vim python3-numpy python3-matplotlib python3-watchdog python3-schedule python3-flask

# build metamap lite
COPY ./metamap_install_files /opt/metamap_install_files
RUN cd /opt && \
    unzip /opt/metamap_install_files/public_mm_lite_3.6.2rc8_binaryonly.zip && \
    unzip /opt/metamap_install_files/public_mm_data_lite_usabase_2022aa.zip && \
    unzip /opt/metamap_install_files/public_mm_data_lite_usabase_2022ab.zip



# create mailbox structure
RUN mkdir /opt/mailboxes/
RUN mkdir /opt/mailboxes/brat2csv_archive
RUN mkdir /opt/mailboxes/brat2csv_inbox
RUN mkdir /opt/mailboxes/cds_archive
RUN mkdir /opt/mailboxes/cds_inbox
RUN mkdir /opt/mailboxes/cds_outbox
RUN mkdir /opt/mailboxes/log
RUN mkdir /opt/mailboxes/metamap_inbox
RUN mkdir /opt/mailboxes/pds_archive
RUN mkdir /opt/mailboxes/pds_inbox
RUN mkdir /opt/mailboxes/pds_outbox
RUN mkdir /opt/mailboxes/pds_working

COPY ./brat2csv /opt/brat2csv
COPY ./cds /opt/cds
COPY ./com /opt/com
COPY ./mailboxes/ed_reports /opt/mailboxes/ed_reports
COPY ./mailboxes/metamap_archive /opt/mailboxes/metamap_archive
COPY ./mailboxes/pds_working /opt/mailboxes/pds_working
COPY ./models /opt/models
COPY ./PDS /opt/PDS
COPY ./web_ui /opt/web_ui

WORKDIR /opt/com

# make the start script executable and run it as the container command
RUN chmod +x /opt/com/start_services.sh

CMD ["/opt/com/start_services.sh"]
