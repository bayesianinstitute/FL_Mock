# Mqtt_Comm_Test
MQTT and Experiment

## Overview
This project is focused on MQTT communication ,IPFS , Decentralized FL.

## Getting Started
To run the project, you can use the following steps:



### Installation
1. Install pip and virtual env
```bash
sudo apt install python3-pip
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
#### Install IPFS 

```
bash run install_ipfs.sh
```

#### Run IPFS 

```
bash run run_ipfs.sh
``` 


### Clone this repository to your local machine.

```
https://github.com/bayesianinstitute/FL_Mock.git
```

Navigate to the project directory.
```
cd FL_Mock
```


### Running the Project

#### For Linux
```
bash run.sh your-id
```
Example

```
bash run.sh 3
```

#### For Windows
```
run.bat your-id
```
Example

```
run.bat 3
```
### For All OS

```
python main.py USA internal_USA_topic 1
```



### Core Functions
The project's core contains the main MqttCluster class that handles the MQTT cluster communication. The core functionalities include:

Creating and managing MQTT clients.
Running the logic for the cluster.