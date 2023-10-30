

# MQTT Participant Identification Script

## Overview

This Python script is designed to identify a participant in a distributed system and potentially declare one of them as an aggregator based on RAM usage. It uses the Paho MQTT library to connect to an MQTT broker and share RAM usage information with other participants.

## Usage

1. Install required Python packages:


2. Run the script with the following command:

```
python identify_participant.py [client_id]
```


Replace `[client_id]` with a unique identifier for your machine.

3. The script will connect to the MQTT broker (broker.hivemq.com by default) and subscribe to two topics: "ram_topicc" and "aggregator_topicc." It will also publish RAM usage information and check for other participants' RAM usage.

4. The script will keep running until it either becomes the aggregator (if RAM usage is the highest) or until it observes the minimum number of participants required (5 by default). Once the conditions are met, it will declare itself as the aggregator and print a message. The script will exit at this point.

5. If the script is not the aggregator, it will continue to run and periodically announce its RAM usage.

## MQTT Topics

- `ram_topicc`: Used for sharing RAM usage information with other participants.
- `aggregator_topicc`: Used for declaring the aggregator.

## Configuration

You can modify the following parameters in the script:

- `broker`: MQTT broker hostname (default: broker.hivemq.com).
- `ram_topic`: The topic for sharing RAM usage information.
- `aggregator_topic`: The topic for declaring the aggregator.
- `Minimum_participate`: The minimum number of participants required to start the process (default: 5).





Returns:
A list of participants identified in the DFL process.

## Usage

1. Clone this repository to your local machine:

```
    git clone https://github.com/bayesianinstitute/FL_Mock.git
```

2. Navigate to the script's directory:

```
  cd core/FL_System/identifyparticipants
```

3. Run the script:

```
    python3 identify_participants.py 1
```
