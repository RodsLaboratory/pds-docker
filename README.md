# PDS Docker

This repository contains Dockerfiles and related resources for building a Docker image of the Probabilistic Disease
Surveillance System (PDS).

# Prerequisites

- The PDS Docker source code, which can be cloned from this repository.
- Docker installed on your system and working knowledge of building and running containers. You can download it
  from [Docker's official website](https://www.docker.com/get-started).
- A license to the UMLS so that you can download Metathesaurus files for Metamap Lite.  You can obtain a license by
visiting: https://uts.nlm.nih.gov/uts/signup-login

# PDS Docker System

The container contains a full PDS system, which includes the following components:
* Metamap Lite: Processes text files to extract medical concepts. 
* ED reports that the system can process 
* brat2csv: Converts Metamap Lite output files to arff format. 
* CDS System: Runs multiple disease models on the extracted medical concepts and classifies each patient for each
   disease. 
* Models of diseases for the CDS system 
* ILI Tracker: Analyzes CDS output to detect known and unknown outbreaks. 
* A web-based user interface to demonstrate the PDS system.

# Walkthrough

This walkthrough will guide you through setting up and running the PDS Docker container.

## Clone the repository
First, clone the PDS Docker repository to your local machine:

```bash
git clone https://github.com/RodsLaboratory/pds-docker.git
```

## Set Up UMLS Metathesaurus Files
- Download the following:
  - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_lite_3.6.2rc6_binaryonly.zip
  - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_data_lite_usabase_2020aa.zip
  - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_data_lite_usabase_2020ab.zip
- Move or copy the downloaded UMLS Metathesaurus and Metamap Lite zip files to the directory ```metamap_install_files```

## Build the Image

To build the Docker images, open a terminal or command line session, navigate to the base directory of the PDS Docker project and
run the docker build command:

```bash
cd <path_to_PDS_Docker_project>
docker build -t pds_image .
```

## Run the Docker Container

To run the Docker container and expose the web-based user interface (on local port 5001), use the following command:

```bash
docker run  --name pds_container -p 127.0.0.1:5001:5001 pds_image
```

To stop the container press Ctrl-C in the terminal where the container is running.

## View the PDS System Demonstration

Once the container is running visit http://127.0.0.1:5001 in your web browser to view the PDS system demonstration
interface.

# Processing your own ED reports

To process your own ED reports, you will need to mount the mailboxes folders in the container to your system. Use the
following command to run the container with mounted volumes:

```bash
docker run  --name pds_container -p 127.0.0.1:5001:5001 -v <path_to_PDS_Docker_project>:/opt/mailboxes pds_image
```

Then copy ED report text files into the ```<path_to_PDS_Docker_project>/metamap_inbox``` folder on your system. The container
will process the files and display the results in the web interface.

