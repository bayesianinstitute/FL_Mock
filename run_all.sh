#!/bin/bash

# Function to check if a command is available
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

install_ipfs() {
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
}

# Check if IPFS is installed
if command_exists ipfs; then
  echo "IPFS is already installed. Running IPFS daemon..."

  # Run IPFS daemon
  start ipfs daemon
else
  install_ipfs
fi

# Continue with the rest of the script...

# cd FL_Mock
cd FL_Mock || exit
git pull

# Install Python virtual environment
sudo apt install python3.10-venv

python3 -m venv myenv

# Activate virtual environment
source myenv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run Django server
python3 db/manage.py runserver 

# Run mlflow
cd core/MLOPS/Model/
# Run mlflow with host as 0.0.0.0 and port as 5000
mlflow ui --host 0.0.0.0 --port 5000

# Run the main program
python3 main.py test.mosquitto.org USA 
