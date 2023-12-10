import paho.mqtt.client as mqtt
import json
import time

SEND_NETWORK_STATUS = "SendNetworkStatus"
SEND_TRAINING_STATUS = "SendTrainingStatus"
TRAIN_MODEL = "TrainModel"
RECEIVE_MODEL_INFO = "ReceiveModelInfo"
TERMINATE_API = "TerminateAPI"
PAUSE_API = "PauseAPI"
RESUME_API = "ResumeAPI"
SEND_GLOBAL_MODEL_HASH = "SendGlobalModelHASH"

topics = 'internal_cluster_topic'
import random

id = random.randint(0,100)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topics, qos=2)

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

def send_network_status():
    message_json = json.dumps({
        "receiver": 'Admin',
        "role": 'User',
        "msg": SEND_NETWORK_STATUS,
        "node_id": 1,
        "network_status": "connected",
    })

    return message_json

def send_model_to_internal_cluster():
    message_json = json.dumps({
        "receiver": 'Admin',
        "role": 'User',
        "msg": RECEIVE_MODEL_INFO,
        "node_id": id,
        "model_hash": "Faijan hahs",
        "accuracy": "500000",
        "loss": "3",
    })
    return message_json

def send_training_status():
    message_json = json.dumps({
        "receiver": 'Admin',
        "role": 'User',
        "msg": SEND_TRAINING_STATUS,
        "training_status": 'training_status',
        "node_id": id,

    })
    return message_json
if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    will_set_msg = json.dumps({
        "receiver": 'Admin',
        "msg": "Disconnected-Node",
        "id": id,
    })

    client.will_set(topics, will_set_msg, qos=2)

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
