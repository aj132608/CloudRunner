#!/bin/bash

sudo touch startup_init

# Set up Logging
touch ec2_worker_logfile.txt
exec > >(tee -i ec2_worker_logfile.txt)
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