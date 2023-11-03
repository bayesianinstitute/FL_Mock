import paho.mqtt.client as mqtt
import argparse

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to the broker")
        # Subscribe to a topic
        client.subscribe("your/subscription/topic")
        # Publish a message
        client.publish("your/publish/topic", "Hello, MQTT!")
    else:
        print(f"Unable to connect to the broker, result code: {rc}")

def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"Unexpected disconnection with result code {rc}")
        # Publish the "last will" message
        last_will_topic = "your/last/will/topic"
        last_will_message = "Client disconnected unexpectedly"
        client.publish(last_will_topic, last_will_message, qos=1, retain=True)
    else:
        print("Unexpected disconneted")
def main():
    parser = argparse.ArgumentParser(description="MQTT Client")
    parser.add_argument("--client-id", type=str, help="Client ID for MQTT connection")
    args = parser.parse_args()

    # Create an MQTT client
    client = mqtt.Client(client_id=args.client_id)

    # Set the on_connect and on_disconnect callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Connect to the broker
    client.connect("localhost", 1883)

    # Start the client loop
    client.loop_start()

    # Keep the program runningANN-Classification
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass

    # When you're done, disconnect the client
    client.disconnect()

if __name__ == "__main__":
    main()
