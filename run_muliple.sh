#!/bin/bash

# Function to run IPFS commands on a specific instance
run_ipfs_commands() {
  instance_address="$1"
  ssh -i "$private_key" "$instance_address" "
    ipfs shutdown
    ipfs init
    ipfs daemon
  "
}

# Define an array of private key files and corresponding instance addresses
private_keys=("mqtt_fl_client_2.pem" "mqtt_fl_client_3.pem" "mqtt_fl_client_4.pem")
instance_addresses=("ubuntu@ec2-54-183-13-28.us-west-1.compute.amazonaws.com" "ubuntu@ec2-52-8-56-54.us-west-1.compute.amazonaws.com" "ubuntu@ec2-54-176-41-237.us-west-1.compute.amazonaws.com")

# Export the function to make it available in child shells
export -f run_ipfs_commands

# Loop through the instances and execute IPFS commands with the specified private keys and instance addresses
for ((i = 0; i < ${#private_keys[@]}; i++)); do
  gnome-terminal -- bash -c "run_ipfs_commands \"${instance_addresses[$i]}\"; read -p 'Press Enter to close this terminal...'"
done

# Function to run the main script for a specific private key and instance address
run_script() {
  private_key="$1"
  instance_address="$2"
  id="$3"

  ssh -i "$private_key" "$instance_address" "
    cd FL_Mock &&
    git pull &&
    source myenv/bin/activate &&
    pip install -r requirements.txt &&
    python main.py USA internal_USA_topic $id
  "
}

# Export the function to make it available in child shells
export -f run_script

# Loop through the instances and execute the main script with the specified private keys and instance addresses
for ((i = 0; i < ${#private_keys[@]}; i++)); do
  id=$((i + 1))
  gnome-terminal -- bash -c "run_script \"${private_keys[$i]}\" \"${instance_addresses[$i]}\" \"$id\"; read -p 'Press Enter to close this terminal...'"
done
