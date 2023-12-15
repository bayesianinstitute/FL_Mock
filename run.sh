#!/bin/bash

# Hardcoded MQTT broker
MQTT_BROKER="test.mosquitto.org"

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <TRAINING_NAME> <ROLE>"
    exit 1
fi

# Assigning arguments to variables
TRAINING_NAME=$1
ROLE=$2

# Run the Python script with the provided parameters
python.exe main.py $MQTT_BROKER $TRAINING_NAME $ROLE
