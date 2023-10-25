import paho.mqtt.client as mqtt
import time
import subprocess
import json
import random
import psutil  # Import the psutil library

import paho.mqtt.client as mqtt
import time
import subprocess
import json
import random
import psutil  # Import the psutil library

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("ram_topic")

def on_message(client, userdata, message):
    ram_info = json.loads(message.payload.decode("utf-8"))
    node_id = ram_info["node_id"]
    ram_usage = ram_info["ram_usage"]
    print(f"Received RAM usage from {node_id}: {ram_usage} MB")
    userdata[node_id] = ram_usage

def announce_ram_usage(client, participant_id, ram_usage):
    topic = 'ram_topic'
    ram_info = {
        "node_id": participant_id,
        "ram_usage": ram_usage
    }
    client.publish(topic, json.dumps(ram_info))

def declare_aggregator(client, participant_id):
    topic = 'aggregator_topic'
    aggregator_message = f"Machine {participant_id} is the aggregator!"
    client.publish(topic, aggregator_message)

def measure_ram_usage():
    try:
        ram_usage = psutil.virtual_memory().used / (1024 ** 2)  # Get RAM usage in MB
        print("ram_usage : {ram_usage} MB",ram_usage)
        return ram_usage
    except Exception as e:
        print(f"Error measuring RAM usage: {str(e)}")
    return 0  # Default to 0 if measurement fails

def main():
    broker = 'test.mosquitto.org'
    participant_id = f"Machine-id- {random.randint(1, 1000)}"  # Unique identifier for each machine

    time.sleep(30)
    print("my id ",participant_id)

    client = mqtt.Client(userdata={"ram_usages": {}, "shared_count": 0},clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, 1883)
    client.loop_start()

    # Measure the node's RAM usage
    ram_usage = measure_ram_usage()

    # Announce RAM usage
    announce_ram_usage(client, participant_id, ram_usage)

    while True:
        shared_count = client._userdata["shared_count"]
        if shared_count < 2:
            time.sleep(10)  # Wait for more clients to share data
        else:
            # Check if this node has the highest RAM usage
            ram_usages = client._userdata["ram_usages"]
            if is_highest_ram_usage(ram_usage, ram_usages):
                declare_aggregator(client, participant_id)
                print(f"I am the aggregator! RAM usage: {ram_usage} MB")
                break

def is_highest_ram_usage(current_ram_usage, ram_usages):
    # Check if current_ram_usage is equal to or higher than the highest RAM usage
    max_ram_usage = max(ram_usages.values())
    return current_ram_usage >= max_ram_usage

if __name__ == '__main__':
    main()


def measure_ram_usage():
    try:
        ram_usage = psutil.virtual_memory().used / (1024 ** 2)  # Get RAM usage in MB
        print("ram_usage : {ram_usage} MB",ram_usage)
        return ram_usage
    except Exception as e:
        print(f"Error measuring RAM usage: {str(e)}")
    return 0  # Default to 0 if measurement fails

def main():
    broker = 'test.mosquitto.org'
    participant_id = f"Machine-id- {random.randint(1, 1000)}"  # Unique identifier for each machine

    print("my id ",participant_id)

    client = mqtt.Client(userdata={"ram_usages": {}, "shared_count": 0})
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, 1883)
    client.loop_start()

    # Measure the node's RAM usage
    ram_usage = measure_ram_usage()

    # Announce RAM usage
    announce_ram_usage(client, participant_id, ram_usage)

    while True:
        shared_count = client._userdata["shared_count"]
        if shared_count < 2:
            time.sleep(10)  # Wait for more clients to share data
        else:
            # Check if this node has the highest RAM usage
            ram_usages = client._userdata["ram_usages"]
            if is_highest_ram_usage(ram_usage, ram_usages):
                declare_aggregator(client, participant_id)
                print(f"I am the aggregator! RAM usage: {ram_usage} MB")
                break

def is_highest_ram_usage(current_ram_usage, ram_usages):
    # Check if current_ram_usage is equal to or higher than the highest RAM usage
    max_ram_usage = max(ram_usages.values())
    return current_ram_usage >= max_ram_usage

if __name__ == '__main__':
    main()
