# PDS Docker

This repository contains Dockerfiles and related resources for building Docker images used in the Probabilistic Disease Surveillance System (PDS).

# Prerequisites
- The PDS source code, which can be cloned from this repository.
- Docker installed on your system. You can download it from [Docker's official website](https://www.docker.com/get-started).
- An unzip utility such as `unzip` or `7zip` to extract UMLS Metathesaurus files.
- UMLS Metathesaurus files for Metamap Lite (requires UMLS license). You can obtain these files from the following links:
  - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_data_lite_usabase_2020aa.zip
  - https://data.lhncbc.nlm.nih.gov/umls-restricted/ii/tools/MetaMap/download/metamaplite/public_mm_data_lite_usabase_2020ab.zip

# Building the Docker Images
## Set Up UMLS Metathesaurus Files
- Download the UMLS Metathesaurus files from the links provided above.
- Move or copy the downloaded zip files to the root of the PDS source code directory.
- Unzip the downloaded files to the root of the PDS source code directory.
## Build the Images
   To build the Docker images, navigate to the root of the PDS Docker project and run the following command:

```bash
docker build -t pds_image .
```
# Running the Docker Container
To run the Docker container, use the following command:
```bash
docker run --name pds_container -v {path to}/mailboxes:/opt/mailboxes pds_image
```

