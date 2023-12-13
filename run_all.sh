#!/bin/bash

# Function to check if a command is available
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check if IPFS is installed
if command_exists ipfs; then
  echo "IPFS is already installed. Running IPFS daemon..."

  # Run IPFS daemon
  start ipfs daemon
else
  echo "IPFS is not installed. Installing IPFS..."

  # Install IPFS
  sudo apt update
  sudo apt install snapd
  curl -L -o kubo_v0.23.0_linux-amd64.tar.gz https://dist.ipfs.tech/kubo/v0.23.0/kubo_v0.23.0_linux-amd64.tar.gz
  tar -xvzf kubo_v0.23.0_linux-amd64.tar.gz
  cd kubo || exit
  sudo bash install.sh
  ipfs --version
  ipfs init
fi

# Your existing script follows...

# cd FL_Mock
git pull

# Activate virtual environment
source myenv/bin/activate

pip install -r requirements.txt

# Run Django server
start python db/manage.py runserver

# Run mlflow
start mlflow ui -H localhost -p 5000

# Run main program
start python core/MLOPS/Model/main.py test.mosquitto.org USA $1 1
