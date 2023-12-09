import paho.mqtt.client as mqtt
import json
import time

SEND_NETWORK_STATUS = "SendNetworkStatus"
SEND_TRAINING_STATUS = "SendTrainingStatus"
TRAIN_MODEL = "TrainModel"
RECEIVE_MODEL_INFO = "ReceiveModelInfo"
TERMINATE_API = "TerminateAPI"
PAUSE_API = "PauseAPI"

topics = 'internal_cluster_topic'
import random

id = random.randint(0,10)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topics, qos=2)

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

def send_network_status():
    message_json = json.dumps({
        "receiver": 'Admin',
        "msg": SEND_NETWORK_STATUS,
        "client_id": id,
        "network_status": "active",
    })
    return message_json

def send_model_to_internal_cluster():
    message_json = json.dumps({
        "receiver": 'Admin',
        "msg": RECEIVE_MODEL_INFO,
        "client_id": id,
        "model_hash": "Faijan hahs",
        "accuracy": "500000",
        "loss": "3",
    })
    return message_json

def send_training_status():
    message_json = json.dumps({
        "receiver": 'Admin',
        "msg": SEND_TRAINING_STATUS,
        "training_status": 'training_status',
        "client_id": id,

    })
    return message_json

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    broker_address = "test.mosquitto.org"
    port = 1883

    role = "User"

    client.connect(broker_address, port, 60)
    client.loop_start()

    while True:
        try:
            # Call your message-sending methods and publish the resulting JSON
            client.publish(topics, send_network_status(), qos=2)
            client.publish(topics, send_training_status(), qos=2)

            time.sleep(5)   

            client.publish(topics, send_model_to_internal_cluster(), qos=2)

            print("Successfully sent messages to admin")
            time.sleep(id)


        except KeyboardInterrupt:
            client.disconnect()
            print("Disconnected.")
            break
