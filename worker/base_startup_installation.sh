#!/bin/bash

# Set up Logging
mkdir /.mineai
mkdir /.mineai/configs

chmod 777 /.mineai
chmod 777 /.mineai/configs

touch /.mineai/worker_startup_logfile.txt
exec > >(tee -i /.mineai/worker_startup_logfile.txt)
exec 2>&1

# Install Git
sudo apt-get update
sudo apt-get install -y git-core

# Install Inotify
sudo apt-get install -y inotify-tools

