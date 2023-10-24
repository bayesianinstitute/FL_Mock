import paho.mqtt.client as mqtt
import json
from sklearn.linear_model import LinearRegression
import numpy as np

# Define the MQTT parameters
broker_address = "test.mosquitto.org"  # Replace with your MQTT broker address
port = 1883
topic = "model_topic"

# Create and train a simple linear regression model (replace this with your own model)
X = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)
y = np.array([2, 4, 5, 4, 5])
model = LinearRegression()
model.fit(X, y)

# Serialize the model parameters to a dictionary
model_params = {
    "coef_": model.coef_.tolist(),
    "intercept_": model.intercept_.tolist(),
}

# Create an MQTT client
client = mqtt.Client("ModelPublisher")

try:
    # Connect to the MQTT broker
    client.connect(broker_address, port)

    # Publish the model parameters to the MQTT topic as JSON
    client.publish(topic, payload=json.dumps(model_params), qos=1)

    # Disconnect from the MQTT broker
    client.disconnect()

except Exception as e:
    print("An error occurred:", str(e))
