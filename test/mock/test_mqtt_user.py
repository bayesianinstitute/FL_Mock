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

id = random.randint(0, 100)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topics, qos=2)

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    # Add logic to handle pause and resume messages if needed

def send_global_model():
    message_json = json.dumps({
        "receiver": 'User',
        "role": 'Admin',
        "msg": SEND_GLOBAL_MODEL_HASH,
        "Admin": id,
        "global_hash": 'QmbWLHYpFhvbD1BB67TfbHisesuq5VutDC5LYEGTxpgATB'
    })
    return message_json

def send_terminate_message():
    message_json = json.dumps({
        "receiver": 'User',
        "role": 'Admin',

        "msg": TERMINATE_API,
        "Admin": id
    })
    return message_json

def send_pause_message():
    message_json = json.dumps({
        "receiver": 'User',
        "role": 'Admin',

        "msg": PAUSE_API,
        "Admin": id
    })
    return message_json

def send_resume_message():
    message_json = json.dumps({
        "receiver": 'User',
        "role": 'Admin',
        "msg": RESUME_API,
        "Admin": id
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

            time.sleep(9)

            client.publish(topics, send_global_model(), qos=2)
            print("Successfully sent Global Model to User")

            time.sleep(4)

            client.publish(topics, send_pause_message(), qos=2)

            time.sleep(8)

            client.publish(topics, send_resume_message(), qos=2)

            time.sleep(8)

            client.publish(topics, send_terminate_message(), qos=2)


            

        except KeyboardInterrupt:
            client.disconnect()
            print("Disconnected.")
            break