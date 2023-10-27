#!/bin/bash

# Check if 'id' argument is provided
if [ -z "$1" ]; then
  echo "Please provide the 'id' argument."
  exit 1
fi

# Execute main.py with the 'id' argument
python main.py USA internal_USA_topic "$1"
