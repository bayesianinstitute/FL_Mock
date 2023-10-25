import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("$SYS/broker/clients/connected")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} - {msg.payload.decode()}")

# Define MQTT broker information
mqtt_broker = "localhost"
mqtt_port = 1883

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)
client.subscribe("response/connected-devices")

# Publish a request to get the list of connected devices
client.publish("request/connected-devices", "Please provide the list of connected devices")

client.loop_forever()
