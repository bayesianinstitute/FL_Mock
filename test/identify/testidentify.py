import paho.mqtt.client as mqtt
import time
import subprocess
import json
import random

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("speed_topic")

def on_message(client, userdata, message):
    speed_info = json.loads(message.payload.decode("utf-8"))
    node_id = speed_info["node_id"]
    download_speed = speed_info["download_speed"]
    print(f"Received speed from {node_id}: {download_speed} Mbps")
    userdata[node_id] = download_speed

def announce_speed(client, participant_id, download_speed):
    topic = 'speed_topic'
    speed_info = {
        "node_id": participant_id,
        "download_speed": download_speed
    }
    client.publish(topic, json.dumps(speed_info))

def declare_aggregator(client, participant_id):
    topic = 'aggregator_topic'
    aggregator_message = f"Machine {participant_id} is the aggregator!"
    client.publish(topic, aggregator_message)

def measure_bandwidth():
    try:
        # Use the speedtest-cli library to measure bandwidth
        result = subprocess.check_output(["speedtest-cli", "--simple"]).decode("utf-8")
        for line in result.split('\n'):
            if "Download" in line:
                download_speed = float(line.split(':')[1].split()[0])
                return download_speed
    except Exception as e:
        print(f"Error measuring bandwidth: {str(e)}")
    return 0  # Default to 0 if measurement fails

def main():
    broker = 'test.mosquitto.org'
    participant_id = f"Machine1 - {random.randint(1,1000)}"  # Unique identifier for each machine

    client = mqtt.Client(userdata={"speeds": {}, "shared_count": 0})
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker,1883)
    client.loop_start()

    # Measure the node's bandwidth
    download_speed = measure_bandwidth()

    # Announce speed
    announce_speed(client, participant_id, download_speed)

    while True:
        shared_count = client.user_data["shared_count"]
        if shared_count < 3:
            time.sleep(10)  # Wait for more clients to share data
        else:
            # Check if this node has the highest bandwidth speed
            speeds = client.user_data["speeds"]
            if is_highest_bandwidth_speed(download_speed, speeds):
                declare_aggregator(client, participant_id)
                print(f"I am the aggregator! Bandwidth: {download_speed} Mbps")
                break

def is_highest_bandwidth_speed(current_speed, speeds):
    # Check if current_speed is the highest among all participants' speeds
    max_speed = max(speeds.values())
    return current_speed == max_speed

if __name__ == '__main__':
    main()
