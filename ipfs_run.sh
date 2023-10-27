sudo apt update
sudo apt install snapd



curl -L -o kubo_v0.23.0_linux-amd64.tar.gz https://dist.ipfs.tech/kubo/v0.23.0/kubo_v0.23.0_linux-amd64.tar.gz
tar -xvzf kubo_v0.23.0_linux-amd64.tar.gz
cd kubo
sudo bash install.sh
ipfs --version

ipfs init

ipfs daemon

