import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        # Subscribe to the topic where the broker publishes information about connected clients
        client.subscribe("$SYS/broker/clients/total")
    else:
        print(f"Connection failed with code {rc}")

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed with QoS: {granted_qos}")

def on_message(client, userdata, msg):
    print(f"Received message on topic '{msg.topic}': {msg.payload.decode()}")

# Replace with the actual broker address and port
broker_address = "test.mosquitto.org"
broker_port = 1883

client = mqtt.Client()
client.on_connect = on_connect
client.on_subscribe = on_subscribe
client.on_message = on_message

client.connect(broker_address, broker_port, 60)

# Start the MQTT loop to listen for messages
client.loop_start()

# Keep the script running
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Disconnecting from the broker")
    client.disconnect()
    client.loop_stop()
