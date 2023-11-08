# Mqtt_Comm_Test

MQTT and Experiment

## Overview

This project is focused on MQTT communication ,IPFS , Decentralized FL.

## Getting Started

To run the project, you can use the following steps:

### Directly Installed

Note that in your current directory you should have all AWS System .PEM Keys to run the code

```bash
bash run_multiple.sh
```

### Installation

### Clone this repository to your local machine.

```
https://github.com/bayesianinstitute/FL_Mock.git
```

Navigate to the project directory.

```
cd FL_Mock
```

1. Install pip and virtual env

```bash
sudo pip install virtualenv
```

2. Create a virtual environment

```bash
virtualenv myenv
```

3. Activate the Virtual Environment:
   To activate the virtual environment, run:

```bash
source myenv/bin/activate
```

4. Install Packages and Run Your Project:
   After activating the virtual environment, you can install packages and run your project as usual:

```bash
pip install -r requirements.txt
```

#### Run IPFS

```
bash run run_ipfs.sh
```

### For All OS

To run the script, use the following command:

```
bash run.sh "your_id"
```
Your id replace with id 

#### Example


```
bash run.sh 1
```

## Workflow

The DFL workflow implemented in this script consists of the following steps:

- Participant identification.
- MQTT setup and communication.
- Training machine learning models.
- Aggregation of models (if the participant is the aggregator).
- Model validation and iteration.
- The workflow can be customized based on your specific use case and requirements.

### Core Functions

The project's core contains the main MqttCluster class that handles the MQTT cluster communication. The core functionalities include:

Creating and managing MQTT clients.
Running the logic for the cluster.
