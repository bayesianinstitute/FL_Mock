import paho.mqtt.client as mqtt
import json
import time

admin_to_client_topic = "admin_to_client_topic"
client_to_admin_topic = "client_to_admin_topic"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(client_to_admin_topic)  # Fix the topic here
    client.subscribe(admin_to_client_topic) # Fix the topic here

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    broker_address = "test.mosquitto.org"
    port = 1883

    role = "User"

    message = {
        "id": 7,
        "role": role,
    }

    data = json.dumps(message)
    print(data)

    client.connect(broker_address, port, 60)
    client.loop_start()

    while True:
        try:
            client.publish(client_to_admin_topic, data, qos=1)
            print("Successfully sent message to admin")

            client.publish(admin_to_client_topic, data, qos=1)
            print("Successfully sent message to user")

            time.sleep(8)

        except KeyboardInterrupt:
            client.disconnect()
            print("Disconnected.")
            break
