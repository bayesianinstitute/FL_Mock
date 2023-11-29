import paho.mqtt.client as mqtt

# MQTT settings
mqtt_broker_address = 'test.mosquitto.org'
mqtt_topic_subscribe = 'your_topic_subscribe'

# MQTT callback for when a message is received
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"Received message: {payload}")

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
