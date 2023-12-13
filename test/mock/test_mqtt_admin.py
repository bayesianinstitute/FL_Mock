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


JOIN_OPERATION = "JoinOperation"

GRANTED_JOIN = "Granted_JOIN"

cluster_name="USA"
topics=f'{cluster_name}_topic'

import random

id = 5
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topics, qos=2)

def on_message(client, userdata, msg):
    message_data = json.loads(msg.payload.decode())
    nodeid=message_data.get("node_id")

    if nodeid==id:
        print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")



        msg_type = message_data.get("msg")
        if msg_type == GRANTED_JOIN:
            handle_config(message_data)



def send_network_status():
    message_json = json.dumps({
        "receiver": 'Admin',
        "role": 'User',
        "msg": SEND_NETWORK_STATUS,
        "node_id": id,
        "network_status": "connected",
    })

    return message_json

def handle_config(data):
    Model_type=data.get('model_name')
    optimizer=data.get('optimizer')
    dataset=data.get('dataset_name')
    print(Model_type)
    print(dataset)
    print(optimizer)



    


def process_initial_message(data):
        try:
            if isinstance(data, str):
                message_data = json.loads(data)
            elif isinstance(data, bytes):
                message_data = json.loads(data.decode('utf-8'))
            else:
                message_data = data.get()

            msg_type = message_data.get("msg")

            if msg_type == GRANTED_JOIN:
                handle_config(message_data)

        except json.JSONDecodeError as e:
             pass
            # self.logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
             pass
            # self.logger.error(f"Error in process_received_message: {str(e)}")
            # time.sleep(10)

def join_training_network( ):
      
    message_json = json.dumps({
                    "receiver": 'Admin',
                    "role": 'User',
                    "training_name": cluster_name,
                    "msg": JOIN_OPERATION,
                    "node_id": id,
                })
    
    return message_json


def send_model_to_internal_cluster():
    message_json = json.dumps({
        "receiver": 'Admin',
        "msg": RECEIVE_MODEL_INFO,
        "node_id": id,
        "model_hash": "'QmeckrNjvpqGfWywVtdt6RW1eQAamxFf1UZ8QBh8dsbADf",
        "accuracy": "500000",
        "loss": "3",
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
            client.publish(topics, join_training_network(), qos=2)

            time.sleep(6)

            client.publish(topics,send_network_status(),qos=2)   
            time.sleep(4)


            client.publish(topics, send_model_to_internal_cluster(), qos=2)

            # print("Successfully sent messages to admin")
            time.sleep(10)

        except KeyboardInterrupt:
            client.disconnect()
            print("Disconnected.")
            break
