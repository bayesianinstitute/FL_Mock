import paho.mqtt.client as mqtt
import time
import argparse

# Define the MQTT broker and topic
broker_address = "localhost"  # Change to your MQTT broker's address
topic = "mytopic"

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe(topic, qos=1)  # Set the subscription QoS to 2
    else:
        print(f"Connection failed with code {rc}")

# Callback when a message is published
def on_publish(client, userdata, mid):
    print(f"id {client._client_id} Message published (mid={mid}) ")

# Callback when a message is received from the broker
def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

def run(client_id):
    # Create an MQTT client
    client = mqtt.Client(client_id=client_id)

    # Set the callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message = on_message

    # Connect to the broker
    client.connect(broker_address, port=1883)

    client.loop_start()

    # Publish a message with QoS 2
    message = f"Hello, MQTT! from {client_id}"
    while True:
        time.sleep(10) 
        client.publish(topic, message, qos=1)  # Set the publishing QoS to 2
        print(f"Publishing message: {message}")
         # Publish a message every 5 seconds

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="MQTT Client", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--id', default="client_id", help="MQTT client ID")
    args = parser.parse_args()

    run(args.id)
