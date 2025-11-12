# Probabilistic Disease Surveillance (PDS)

This repository contains a Dockerfile and related resources for building a Docker image of the Probabilistic Disease
Surveillance System (PDS).

# PDS Docker Container Overview

The container contains a full PDS system, which includes the following components:

* Metamap Lite: Processes text files to extract medical concepts.
* ED reports that the system can process
* brat2csv: Converts Metamap Lite output files to arff format.
* CDS System: Runs multiple disease models on the extracted medical concepts and classifies each patient for each
  disease.
* Models of diseases for the CDS system
* ILI Tracker: Analyzes CDS output to detect known and unknown outbreaks.
* A web-based user interface to demonstrate the PDS system.
* A filewatcher that monitors inboxes for new ED reports to process.

# Prerequisites

- Docker installed on your system and working knowledge of building and running containers. You can download it
  from [Docker's official website](https://www.docker.com/get-started).
- A license to the UMLS so that you can download Metathesaurus files for Metamap Lite. You can obtain a license by
  visiting: https://uts.nlm.nih.gov/uts/signup-login

# Walkthrough

This walkthrough will guide you through setting up and running the PDS Docker container. Here is a slide deck of the
walkthrough: https://docs.google.com/presentation/d/1WLtX5Na-kBBNo9teeU7NunGXjan30eBpihKqZVARZ50/edit?usp=sharing

## Clone the repository

First, clone the PDS Docker repository to your local machine. In a terminal or command line session, run the following
command:

```bash
cd <directory where you want to clone the repo>
git clone https://github.com/RodsLaboratory/pds-docker.git
```

## Set Up UMLS Metathesaurus Files

- Visit: https://lhncbc.nlm.nih.gov/LHC-research/LHC-projects/NLP/MetaMapLite.html
- Download the following:
    - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_lite_3.6.2rc8_binaryonly.zip
    - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_data_lite_usabase_2022ab.zip
    - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_data_lite_usabase_2022aa.zip

- Move or copy the downloaded UMLS Metathesaurus and Metamap Lite zip files to the directory
  ```<path_to_pds-docker_project>/metamap_install_files```

## Build the Image

To build the Docker image, navigate to the base directory of the PDS Docker project and
run the docker build command:

```bash
cd <path_to_pds-docker_project>
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
interface. Follow the instructions on the web page to detect an outbreak.

# Processing your own ED reports

To process your own ED reports, you will need to mount the mailboxes directory to the container. Here is the command to
remove the existing container and then run the container with the mailboxes directory mounted:

```bash
docker container rm pds_container
docker run  --name pds_container -p 127.0.0.1:5001:5001 -v <path_to_pds-docker_project>/mailboxes:/opt/mailboxes pds_image
```

Now you are able to access the mailboxes from the host filesystem. You can copy ED report text files into the
```<path_to_pds-docker_project>/mailboxes/metamap_inbox``` folder. The format of the filenames is
```<YYYYMMDD>_<SEQ>.txt``` where the YYYYMMDD is the date of the report.   The container
will process the files and display the results in the web interface as before.

