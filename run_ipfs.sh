ipfs init

#!/bin/bash

# Check if IPFS is already running
if pgrep ipfs > /dev/null; then
  echo "IPFS daemon is already running."
else
  # Open a new terminal and run IPFS daemon
  ipfs daemon
fi
