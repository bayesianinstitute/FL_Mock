import paho.mqtt.client as mqtt
import requests

url = "http://127.0.0.1:8000/api/v1/create_training_result/"

headers = {
    "Content-Type": "application/json"
}


# MQTT settings
mqtt_broker_address = 'test.mosquitto.org'
mqtt_topic_subscribe = 'your_topic_subscribe'

# MQTT callback for when a message is received
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"Received message: {payload}")
    import json
    
    # Assuming payload is a valid JSON string
    data = json.loads(payload)

    print("data: {}".format(data['data']))

    # Sending a POST request to the API endpoint
    response = requests.post(url, json=data['data'], headers=headers)

    # Check the response
    if response.status_code == 201:  # Assuming 201 means successful creation
        print("Data added successfully.")
    else:
        print(f"Failed to add data. Status code: {response.status_code}")
        print(response.text)



# MQTT client setup
client = mqtt.Client()
client.on_message = on_message

# Connect to the MQTT broker
client.connect(mqtt_broker_address, 1883, 60)

# Subscribe to the MQTT topic
client.subscribe(mqtt_topic_subscribe)

# Start the MQTT loop
client.loop_start()

try:
    # Keep the script running
    while True:
        pass
except KeyboardInterrupt:
    # Disconnect from the MQTT broker on keyboard interrupt
    client.loop_stop()
    client.disconnect()
    print("Script terminated.")
