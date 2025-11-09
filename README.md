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
3. CDS System: Runs multiple disease models on the extracted medical concepts and classifies each patient for each disease.
4. PDS System: Analyzes CDS output to track disease outbreaks and generates visualizations

# Walkthrough 
This walkthrough will guide you through setting up and running the PDS Docker container.

## Set Up UMLS Metathesaurus Files
- Download the UMLS Metathesaurus files from the links provided above.
- Move or copy the downloaded zip files to the directory ```metamap_install_files```
## Build the Image
To build the Docker images, open a terminal or command line session, navigate to the root of the PDS Docker project and run the docker build command:

```bash
cd <path_to_pds_docker_project>
docker build -t pds_image .
```
## Run the Docker Container
To run the Docker container and expose the web-based user interface, use the following command:
```bash
docker run  --name pds_container -p 127.0.0.1:5001:5001 pds_image
```
To stop the container press Ctrl-C in the terminal where the container is running.
## View the PDS System Demonstration
Once the container is running visit http://127.0.0.1:5001 in your web browser to view the PDS system demonstration interface.

# Processing your own ED reports
To process your own ED reports, you will need to mount the mailboxes folders in the container to your system. Use the following command to run the container with mounted volumes:
```bash
docker run  --name pds_container -p 127.0.0.1:5001:5001 -v <path_to_your_reports>:/opt/mailboxes pds_image
```
Then copy ED report text files into the ```<path_to_your_reports>/metamap_inbox``` folder on your system. The container will process the files and display the results in the web interface.

