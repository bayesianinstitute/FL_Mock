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

id = random.randint(0, 100)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topics, qos=2)


def handle_join(data):
    data=json.dumps({
        "receiver": 'User',
        "role": 'Admin',
        "msg": GRANTED_JOIN,
        "model_name": "CNN",
        "dataset_name": "Mnist",
        "optimizer": "Adam",
        "training_name":topics
        })
    
    client.publish(topics,data,qos=2)


def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    message_data = json.loads(msg.payload.decode())
    msg_type = message_data.get("msg")
    if msg_type == JOIN_OPERATION:
        handle_join(message_data)
    # Add logic to handle pause and resume messages if needed

# def send_global_model():
#     message_json = json.dumps({
#         "receiver": 'User',
#         "role": 'Admin',
#         "msg": SEND_GLOBAL_MODEL_HASH,
#         "Admin": id,
#         "global_hash": 'QmbWLHYpFhvbD1BB67TfbHisesuq5VutDC5LYEGTxpgATB'
#     })
#     return message_json

# def send_terminate_message():
#     message_json = json.dumps({
#         "receiver": 'User',
#         "role": 'Admin',

#         "msg": TERMINATE_API,
#         "Admin": id
#     })
#     return message_json

# def send_pause_message():
#     message_json = json.dumps({
#         "receiver": 'User',
#         "role": 'Admin',

#         "msg": PAUSE_API,
#         "Admin": id
#     })
#     return message_json

# def send_resume_message():
#     message_json = json.dumps({
#         "receiver": 'User',
#         "role": 'Admin',
#         "msg": RESUME_API,
#         "Admin": id
#     })
#     return message_json



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


            time.sleep(15)
            # client.publish(topics, send_global_model(), qos=2)
            # print("Successfully sent Global Model to User")

            # time.sleep(4)

            # client.publish(topics, send_pause_message(), qos=2)
            # print("Successfully sent Pause to User")

            # time.sleep(15)


            # client.publish(topics, send_resume_message(), qos=2)
            # print("Successfully sent Resume to User")

            # time.sleep(9)

            # client.publish(topics, send_terminate_message(), qos=2)
            # print("Successfully sent Terimate to User")
            # # break


            

        except KeyboardInterrupt:
            client.disconnect()
            print("Disconnected.")
            break
