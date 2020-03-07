#!/bin/bash

# Set up Logging
touch worker_logfile.txt
exec > >(tee -i worker_logfile.txt)
exec 2>&1

# Install Git
sudo apt-get update
sudo apt-get install -y git-core
