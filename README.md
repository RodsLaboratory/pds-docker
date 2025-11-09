# PDS Docker

This repository contains Dockerfiles and related resources for building Docker images used in the Probabilistic Disease Surveillance System (PDS).

# Prerequisites
- The PDS Docker source code, which can be cloned from this repository.
- Docker installed on your system and working knowledge of building and running containers. You can download it from [Docker's official website](https://www.docker.com/get-started).
- UMLS Metathesaurus files for Metamap Lite (requires UMLS license). You can obtain these files from https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/NLP/MetaMapLite.html:
  - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_lite_3.6.2rc6_binaryonly.zip
  - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_data_lite_usabase_2020aa.zip
  - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_data_lite_usabase_2020ab.zip



# PDS Docker System
The container contains a full PDS system, which includes the following components:
1. Metamap Lite: Processes text files to extract medical concepts.
2. brat2csv: Converts Metamap Lite output files to arff format.
3. CDS System: Processes arff files to generate disease probabilities.
4. PDS System: Analyzes CDS output to track disease outbreaks and generates visualizations

The interface to this container is a series of directories under ./mailboxes:
- metamap_inbox: Place text files to be processed by Metamap Lite here.
- metamap_archive: Processed Metamap Lite input files are archived here.
- brat2csv_inbox: Place Metamap Lite output files here to be converted to arff format
- brat2csv_archive: Processed brat2csv input files are archived here.
- cds_inbox: Place arff files here to be processed by the CDS system.
- cds_archive: Processed CDS input files are archived here.
- pds_inbox: Place CDS output files here (.csv) to be processed by the PDS system.
- pds_archive: Processed PDS input files are archived here.
- pds_outbox: PDS output in the form of png images are placed here.
- pds_working: Working files for PDS are here

You can monitor the processing by checking the contents of these directories.  To start processing copy txt files to metamap_inbox with the file syntax ```<YYYYMMDD>_<sequence number>.txt```.
For your convenience metamap_archive contains sample txt files that you can copy to metamap_inbox to start processing.

After copying the text files to metamap_inbox, you can monitor the progress by checking the contents of the various directories. Processed files will move through the directories as they are processed by each component of the system. The ILI Tracker component runs automatically every minute using data found in pds_working directory. Once the files reach the pds_outbox, you will find the output in the form of png images.

# Walkthrough 
This walkthrough will guide you through setting up and running the PDS Docker container.

## Set Up UMLS Metathesaurus Files
- Download the UMLS Metathesaurus files from the links provided above.
- Move or copy the downloaded zip files to the directory ```metamap_install_files```
## Build the Image
To build the Docker images, navigate to the root of the PDS Docker project and run the following command:

```bash
docker build -t pds_image .
```
## Run the Docker Container
To run the Docker container, use the following command:
```bash
docker run --name pds_container -v {path to}/mailboxes:/opt/mailboxes pds_image
```
1. View the ongoing logs of the running container to monitor processing:
   ```bash
   docker logs -f pds_container
   ```
2. Copy sample text files from `metamap_archive` to `metamap_inbox`:
   ```bash
   cp mailboxes/metamap_archive/*.txt mailboxes/metamap_inbox/
   ```
2. Monitor the processing by checking the contents of the directories.  It will take about an hour to process the sample files:
   ```bash
   ls mailboxes/metamap_inbox
   ls mailboxes/metamap_archive
   ls mailboxes/brat2csv_archive 
   ls mailboxes/cds_archive
   ls mailboxes/pds_archive
   ls mailboxes/pds_outbox
   ```
4. Once the files reach the `pds_outbox`, you will find the output in the form of png images.      
   

