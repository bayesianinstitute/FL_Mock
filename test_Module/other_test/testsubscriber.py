import paho.mqtt.client as mqtt
import json
from sklearn.linear_model import LinearRegression
import numpy as np

# Define the MQTT parameters
broker_address = "test.mosquitto.org"  # Replace with your MQTT broker address
port = 1883
topic = "model_topic"

# Create a callback for when a message is received
def on_message(client, userdata, message):
    model_params = json.loads(message.payload)
    
    # Reconstruct the model from the received JSON
    model = LinearRegression()
    model.coef_ = np.array(model_params["coef_"])
    model.intercept_ = np.array(model_params["intercept_"])
    
    # Use the received model for predictions or other tasks

# Create an MQTT client
client = mqtt.Client("ModelSubscriber")

# Set the on_message callback
client.on_message = on_message

# Connect to the MQTT broker
client.connect(broker_address, port)

# Subscribe to the MQTT topic
client.subscribe(topic)

# Start the MQTT client loop to listen for messages
client.loop_forever()
