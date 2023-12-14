import paho.mqtt.client as mqtt
import json
import time
import random

class MqttUserClient:
    def __init__(self, id, topics, broker_address="test.mosquitto.org", port=1883):
        self.id = id
        self.topics = topics
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Set the last will message
        will_set_msg = json.dumps({
            "receiver": 'Admin',
            "msg": "Disconnected-Node",
            "node_id": self.id,
        })
        self.client.will_set(self.topics, will_set_msg, qos=2)

        self.broker_address = broker_address
        self.port = port

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.topics, qos=2)

    def on_message(self, client, userdata, msg):
        message_data = json.loads(msg.payload.decode())
        nodeid = message_data.get("node_id")

        if nodeid == self.id:
            print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
            msg_type = message_data.get("msg")
            if msg_type == "Granted_JOIN":
                self.handle_config(message_data)

    def send_network_status(self):
        message_json = json.dumps({
            "receiver": 'Admin',
            "role": 'User',
            "msg": "SendNetworkStatus",
            "node_id": self.id,
            "network_status": "connected",
        })
        return message_json

    def handle_config(self, data):
        Model_type = data.get('model_name')
        optimizer = data.get('optimizer')
        dataset = data.get('dataset_name')
        print(Model_type)
        print(dataset)
        print(optimizer)

    def process_initial_message(self, data):
        try:
            if isinstance(data, str):
                message_data = json.loads(data)
            elif isinstance(data, bytes):
                message_data = json.loads(data.decode('utf-8'))
            else:
                message_data = data.get()

            msg_type = message_data.get("msg")

            if msg_type == "Granted_JOIN":
                self.handle_config(message_data)

        except json.JSONDecodeError as e:
            pass
        except Exception as e:
            pass

    def join_training_network(self):
        message_json = json.dumps({
            "receiver": 'Admin',
            "role": 'User',
            "training_name": self.topics,
            "msg": "JoinOperation",
            "node_id": self.id,
        })

        return message_json

    def send_model_to_internal_cluster(self):
        message_json = json.dumps({
            "receiver": 'Admin',
            "msg": "ReceiveModelInfo",
            "node_id": self.id,
            "model_hash": "QmZ5Ld8t2gHxXbESkzKChCXqqaHRxB3Ur8xpxgVFpzidCs",
            "accuracy": "500000",
            "loss": "3",
        })
        return message_json

    def connect_and_start(self):
        self.client.connect(self.broker_address, self.port, 60)
        self.client.loop_start()

        while True:
            try:
                # Call your message-sending methods and publish the resulting JSON
                self.client.publish(self.topics, self.join_training_network(), qos=2)

                time.sleep(6)

                self.client.publish(self.topics, self.send_network_status(), qos=2)
                time.sleep(4)

                self.client.publish(self.topics, self.send_model_to_internal_cluster(), qos=2)
                time.sleep(10)

            except KeyboardInterrupt:
                self.client.disconnect()
                print("Disconnected.")
                break

if __name__ == "__main__":
    user_client = MqttUserClient(id=5, topics="USA_topic")
    user_client.connect_and_start()
