import argparse
import paho.mqtt.client as mqtt
import time

# Define MQTT parameters
broker_address = "localhost"  # You should replace this with your MQTT broker's address
port = 1883
topic = "status"

# Parse the client ID from the command-line arguments
parser = argparse.ArgumentParser(description="MQTT Client with Dynamic Client ID")
parser.add_argument("--client_id", type=str, required=True, help="MQTT client ID")
args = parser.parse_args()

id = args.client_id
print("id: ", id)
# Callback function when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)

# Callback function when a message is received on the "status" topic
def on_message(client, userdata, message):
    print(f"Received message on topic '{message.topic}': {message.payload.decode()}")

# Callback function when the client disconnects
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection. Reconnecting...")
        client.reconnect()

# Initialize the MQTT client with the client ID
client = mqtt.Client(id)

# Set the callback functions
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect to the MQTT broker
client.connect(broker_address, port)

# Start the MQTT loop to handle communication
client.loop_start()

try:
    while True:
        client.publish(topic, f"Client id : {id} is connected")
        time.sleep(5)

finally :
    client.publish(topic, f"Client id : {id} is disconnected")
    client.disconnect()
    client.loop_stop()
    print("Client disconnected.")
