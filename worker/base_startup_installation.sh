#!/bin/bash

sudo touch startup_init

# Set up Logging
touch worker_logfile.txt
exec > >(tee -i worker_logfile.txt)
exec 2>&1

# Install Python
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.7

# Install Git
sudo apt-get install -y git-core

# Install Cloud DSM
#pip install cloud-dsm

# Clone the Cloud DSM git repo
sudo git clone https://mohakamg:c469cbaaafe7a1e2b5339f20b360ca9ffc46c649@github.com/aj132608/CloudRunner.git

# Install Docker
sudo apt-get remove docker docker-engine docker.io
sudo apt install -y docker.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Test Script
sudo docker run -p 9000:9000 -d minio/minio server /data

