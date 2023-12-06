import paho.mqtt.client as mqtt

admin_to_client_topic = "admin_to_client_topic"
client_to_admin_topic = "client_to_admin_topic"


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(admin_to_client_topic)
    client.subscribe(client_to_admin_topic)

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

broker_address = "test.mosquitto.org"
port = 1883

client.connect(broker_address, port, 60)

client.loop_forever()
