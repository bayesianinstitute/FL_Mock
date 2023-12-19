# BAYES DECENTRAZLIED FEDERATED LEARNING

# Technologies 


<!-- Tensorflow Logo -->
![Image Description](doc/static/tensorflow.png)![ImageDescription](doc/static/IPFS.png)![Image Description](doc/static/MQTT.jpg)
![Image Description](doc/static/django.png)![Image Description](doc/static/Sqllite.png)

## Overview

This project is focused on MQTT communication, IPFS,MLFLOW,DJANGO BACKED TO STORE ON LOCAL STORAGE and Decentralized FL.


### AWS Configuration

1. **Create an AWS EC2 Instance:**

   To create an EC2 instance with Ubuntu, machine type t2.2xlarge, and 30 GB SSD storage, follow these steps:

   1. **Open the AWS Management Console:**
      - Go to [AWS Console](https://aws.amazon.com/console/).

   2. **Navigate to EC2:**
      - In the AWS Console, click on "Services" and then select "EC2" under the Compute section.

   3. **Launch an Instance:**
      - Click on the "Instances" link in the left sidebar.
      - Click the "Launch Instances" button.

   4. **Choose an Amazon Machine Image (AMI):**
      - In the "Choose an Amazon Machine Image (AMI)" step, select "Ubuntu" as the operating system.

   5. **Choose an Instance Type:**
      - In the "Choose an Instance Type" step, scroll down and select "t2.2xlarge."

   6. **Configure Instance:**
      - In the "Configure Instance" step, leave the default settings or adjust them as needed.

   7. **Add Storage:**
      - In the "Add Storage" step, set the size to "20 GiB" and choose "SSD" as the volume type.

   8. **Add Tags:**
      - In the "Add Tags" step, add any tags if necessary.

   9. **Configure Security Group:**
      - In the "Configure Security Group" step, configure security group rules to allow incoming traffic on the desired ports (e.g., SSH on port 22, HTTP on port 80, etc.).

   10. **Review and Launch:**
       - In the "Review" step, review your configuration.

   11. **Launch:**
       - Click the "Launch" button.

   12. **Create a Key Pair:**
       - In the pop-up window, select "Create a new key pair" from the drop-down.
       - Enter a key pair name and click "Download Key Pair."

   13. **Launch Instances:**
       - Click the "Launch Instances" button.

   14. **View Instances:**
       - Click on "View Instances" to see the status of your launched instance.

   15. **Connect to the Instance:**
       - Once the instance is running, select the instance, and click the "Connect" button.
       - Follow the instructions to connect using SSH, using the downloaded key pair.

   Your EC2 instance with Ubuntu, machine type t2.2xlarge, and 20 GB SSD storage should now be running. Adjust security group rules and other settings as needed for your specific requirements.

2. **Change Inbound Rules to Open Ports:**

   In the AWS Console, go to the EC2 Dashboard, and select your instance.

   - Click on the "Security" tab.
   - Under "Security groups," click on the associated security group.
   - In the "Inbound rules" tab, add rules to open ports 5000 and 8000 for mlflow and Django server:

     | Type        | Protocol | Port Range | Source    |
     |-------------|----------|------------|-----------|
     | Custom TCP  | TCP      | 5000       | 0.0.0.0/0 |
     | Custom TCP  | TCP      | 8000       | 0.0.0.0/0 |

3. **Allocate and Associate an Elastic IP (Optional):**

   If you want a static IP for your instance, allocate and associate an Elastic IP:

   - In the AWS Console, go to the EC2 Dashboard.
   - Under "Network & Security," click on "Elastic IPs."
   - Allocate a new Elastic IP and associate it with your EC2 instance.


## Getting Started

To run the project, follow the steps below:

### Installation

Clone this repository to your local machine.

```bash
git clone https://github.com/bayesianinstitute/FL_Mock.git
```

Navigate to the project directory.

```bash
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

```bash
source myenv/bin/activate
```

4. Install Packages and Run Your Project:

```bash
pip install -r requirements.txt
```

#### Check and Install IPFS

```bash
bash run run_ipfs.sh
```



### Workflow

The DFL workflow implemented in this script consists of the following steps:

- Participant identification.
- MQTT setup and communication.
- Training machine learning models.
- Aggregation of models (if the participant is the aggregator).
- Model validation and iteration.

The workflow can be customized based on your specific use case and requirements.

### Core Functions

The project's core contains the main MqttOPS class that handles the MQTT cluster communication. The core functionalities include:

- Creating and managing MQTT clients.
- Running the logic for the cluster.

## Additional Steps to Run Dependencies Module

Make sure to pull the latest changes from the repository:

```bash
git pull
```

Run Django server:

Certainly! Here's the modified set of instructions including migrating, makemigrations, creating a superuser, and running the Django server:

```bash

# Create database migrations:
python db/manage.py makemigrations bayes_app

# Migrate the database:
python db/manage.py migrate bayes_app

# Apply migrations:
python db/manage.py migrate

# Create a superuser:
python db/manage.py createsuperuser

# Run Django server:
python db/manage.py runserver 0.0.0.0:8000
```

Make sure to follow these steps after activating the virtual environment. This sequence will migrate the database, create necessary migrations, prompt you to create a superuser, and finally run the Django development server on `0.0.0.0:8000`. Adjust the steps according to your project's requirements.

Run mlflow:

```bash
cd core/MLOPS/Model/
mlflow ui --host 0.0.0.0 --port 5000
```



### How to Run the Program

To execute the main program, follow these steps:

1. Open your terminal.

2. Navigate to the project directory.

3. Use the following command to run the script:

   ```bash
   bash run.sh TRAINING_NAME ROLE
   ```

   Replace `TRAINING_NAME` with the desired training name (e.g., "UCLA") and `ROLE` with either "Admin" or "User."

   Example:

   ```bash
   bash run.sh UCLA User
   ```

   This command initiates the program with the specified training name and role, allowing you to customize the execution based on your requirements.
