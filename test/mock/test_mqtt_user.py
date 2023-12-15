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
global node_id

class MqttClient:
    def __init__(self, cluster_name, broker_address="test.mosquitto.org", port=1883):
        self.cluster_name = cluster_name
        self.topics = f'{cluster_name}_topic'
        self.node_id = None
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Set the last will message
        will_set_msg = json.dumps({
            "receiver": 'Admin',
            "msg": "Disconnected-Node",
            "id": self.node_id,
        })
        self.client.will_set(self.topics, will_set_msg, qos=2)

        self.broker_address = broker_address
        self.port = port

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.topics, qos=2)

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
        message_data = json.loads(msg.payload.decode())
        msg_type = message_data.get("msg")
        if msg_type == JOIN_OPERATION:
            self.handle_join(message_data)

    def handle_join(self, message):
        self.node_id = message.get("node_id")
        data = json.dumps({
            "receiver": 'User',
            "role": 'Admin',
            "msg": GRANTED_JOIN,
            "model_name": "CNN",
            "dataset_name": "Mnist",
            "optimizer": "Adam",
            "training_name": self.topics,
            "node_id": self.node_id
        })

        self.client.publish(self.topics, data, qos=2)
        print(f"Granted to join ID {self.node_id}")
        time.sleep(15)

    def send_global_model(self):
        message_json = json.dumps({
            "receiver": 'User',
            "role": 'Admin',
            "msg": SEND_GLOBAL_MODEL_HASH,
            "Admin": id,
            "global_hash": 'QmYWD59UJdvTXzc3U6pVSS8VB33HqDQZdC2hmHAAHfFHCN'
        })
        return message_json

    def send_resume_message(self):
        message_json = json.dumps({
            "receiver": 'User',
            "role": 'Admin',
            "msg": RESUME_API,
            "Admin": id,
            "node_id": self.node_id

        })
        return message_json

    def send_pause_message(self):
        message_json = json.dumps({
            "receiver": 'User',
            "role": 'Admin',
            "msg": PAUSE_API,
            "node_id": self.node_id
        })
        return message_json
    
    def send_terminate_message(self, ):
        message_json = json.dumps({
                "receiver": 'User',
                "role": 'Admin',
                "node_id": self.node_id,
                "msg": TERMINATE_API,
            })
    
        
        print(f"Terminated API for user {self.node_id}")
        return message_json

    def connect_and_start(self):
        self.client.connect(self.broker_address, self.port, 60)
        self.client.loop_start()

        while True:
            try:
                # Call your message-sending methods and publish the resulting JSON

                time.sleep(15)
                # self.client.publish(self.topics, self.send_global_model(), qos=2)
                # print("Successfully Model")

                time.sleep(8)
                self.client.publish(self.topics, self.send_pause_message(), qos=2)
                print("Successfully sent Resume to User")

                time.sleep(20)
                self.client.publish(self.topics, self.send_terminate_message(), qos=2)
                print("Successfully sent Resume to User")

            except KeyboardInterrupt:
                self.client.disconnect()
                print("Disconnected.")
                break

if __name__ == "__main__":
    mqtt_client = MqttClient(cluster_name="USA")
    mqtt_client.connect_and_start()
