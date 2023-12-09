import paho.mqtt.client as mqtt
import json
import time

SEND_NETWORK_STATUS = "SendNetworkStatus"
SEND_TRAINING_STATUS = "SendTrainingStatus"
TRAIN_MODEL = "TrainModel"
RECEIVE_MODEL_INFO = "ReceiveModelInfo"
TERMINATE_API = "TerminateAPI"
PAUSE_API = "PauseAPI"
SEND_GLOBAL_MODEL_HASH = "SendGlobalModelHASH"

topics = 'internal_cluster_topic'
import random

id = random.randint(0,100)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topics, qos=2)

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

def send_global_model():
    message_json = json.dumps({
        "receiver": 'User',
        "msg": SEND_GLOBAL_MODEL_HASH,
        "Admin": id,
        "global_hash":'QmbWLHYpFhvbD1BB67TfbHisesuq5VutDC5LYEGTxpgATB'

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

            print("Successfully sent GLobal Model to User")


        except KeyboardInterrupt:
            client.disconnect()
            print("Disconnected.")
            break
