import paho.mqtt.client as mqtt
import random
import time
import json
import string

# clients = []
from core.Logs_System.logger import Logger


class MQTTCluster:
    def __init__(self, broker_address, num_clients, cluster_name,  internal_cluster_topic, head_status, id):
        self.logger=Logger(name='MqttCommm_logger').get_logger()
        self.broker_address = broker_address
        self.num_clients = num_clients
        self.cluster_name = cluster_name
        self.worker_head_node = head_status
        self.round = 0
        self.internal_cluster_topic = internal_cluster_topic
        self.client = None
        self.global_model_hash = None
        self.client_hash_mapping = {}
        self.round = 0
        self.id = f"{self.cluster_name}_Client_{id}_{self.generate_random_characters(3)}"
        self.terimate_status = False
        self.head_id=None
        self.switch_Status=False
        self.terim_mid=None
        self.mid=None
        self.admin_to_client_topic = "admin_to_client_topic"
        self.client_to_admin_topic = "client_to_admin_topic"

    def connect_clients(self):
        try:
            self.client = mqtt.Client(self.id)
            self.client.on_message = self.on_message
            self.client.on_publish = self.on_publish
            self.client.on_subscribe = self.on_subscribe

            self.client.connect(self.broker_address, 1883)
            self.client.loop_start()

        except Exception as e:
            self.logger.error(f"Error in connect_clients: {e}")

    def receive_msg(self, role: str):
        try:
            will_set_msg = json.dumps({"Client-disconnected": self.id})

            if role == "Admin":
                self.client.subscribe(self.client_to_admin_topic, qos=1)
                self.client.will_set(self.client_to_admin_topic, will_set_msg, qos=1, retain=False)
            elif role == "User":
                self.client.subscribe(self.admin_to_client_topic, qos=1)
                self.client.will_set(self.admin_to_client_topic, will_set_msg, qos=1, retain=False)

            self.client.connect(self.broker_address, 1883)
            self.client.loop_start()

            return self.id

        except Exception as e:
            self.logger.error(f"Error in receive_msg: {e}")
            return None

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.logger.warning(f"Unexpected disconnection. RC: {rc}")

    def on_message(self, client, userdata, message):
        try:
            client_id = client._client_id.decode('utf-8')
            cluster_id = self.cluster_name
            data = message.payload.decode('utf-8')

            self.logger.debug(f"Received message on topic {message.topic}")
            self.logger.critical(f"data: {data}")

            if message.topic == self.admin_to_client_topic or message.topic == self.client_to_admin_topic:
                self.handle_internal_message(message, client_id, cluster_id, client, message.mid)

        except Exception as e:
            self.logger.error(f"Error in on_message: {e}")

    def send_id(self, role, id):
        try:
            message = {
                "id": id,
                "role": role,
            }
            data = json.dumps(message)
            self.logger.info(data)

            if role == "User":
                self.client.publish(self.client_to_admin_topic, data, qos=1)
            elif role == "Admin":
                self.client.publish(self.admin_to_client_topic, data, qos=1)

            self.logger.debug(f"Successfully sent id: {str(id)} ")

        except Exception as e:
            self.logger.error(f"Error in send_id: {e}")

    def handle_internal_message(self, message, client_id, cluster_id, client, mid):
        try:
            data = message.payload.decode('utf-8')
            json_data = json.loads(data)

            self.logger.info(f"Received data: {json_data}")

            if "head_id" in json_data:
                self.set_head_node_id(json_data)

            if 'global_model' in json_data:
                self.handle_global_model(json_data, client_id, cluster_id)

            if 'msg' in json_data:
                self.handle_client_msg(json_data)

            if self.is_worker_head(client):
                self.handle_internal_data(json_data, client_id, cluster_id)

            if 'terimate_msg' in json_data:
                self.handle_terminate_message(client_id, cluster_id, mid)

        except Exception as e:
            self.logger.error(f"Error in handle_internal_message: {e}")

    def handle_terminate_message(self, client_id, cluster_id, mid):
        try:
            self.terim_mid = mid
            self.logger.critical(f"Terminating id {self.terim_mid} and mid {self.mid}")
            if self.terim_mid == self.mid:
                self.logger.warning(f"Received terminate message from {client_id} in cluster {cluster_id}")
                self.logger.warning(f"ALL Should Disconnected message from client: {client_id}")
                self.terimate_status = True

        except Exception as e:
            self.logger.error(f"Error in handle_terminate_message: {e}")

    def send_terminate_message(self, t_msg):
        try:
            message = {
                "client_id": self.id,
                "terimate_msg": t_msg
            }
            data = json.dumps(message)

            self.client.publish(self.internal_cluster_topic, data, qos=1)
            self.logger.info("Successfully sent send_terminate_message")

        except Exception as e:
            self.logger.error(f"Error in send_terminate_message: {e}")
   


    def handle_global_model(self, json_data, client_id, cluster_id):
        try:
            extract = json_data['global_model']
            self.logger.info(f"Received Global message in {cluster_id} from {client_id} as:\n{extract}")
            self.global_model_hash = extract

        except Exception as e:
            self.logger.error(f"Error in handle_global_model: {e}")

    def handle_internal_data(self, json_data, client_id, cluster_id):
        try:
            if 'Client-disconnected' in json_data:
                self.handle_client_disconnected(json_data)

            if 'client_id' in json_data:
                self.handle_client_data(json_data, cluster_id)

            if 'msg' in json_data:
                self.handle_client_msg(json_data)

        except Exception as e:
            self.logger.error(f"Error in handle_internal_data: {e}")

    def handle_client_msg(self, json_data):
        try:
            self.logger.debug("Checking received msg")
            self.logger.info(json_data)
            time.sleep(10)

        except Exception as e:
            self.logger.error(f"Error in handle_client_msg: {e}")

    def handle_client_disconnected(self, json_data):
        try:
            get_client_id = json_data['Client-disconnected']
            self.logger.warning(f"Disconnected node id: {get_client_id}")
            self.num_clients -= 1
            self.logger.info(f"Remove client from dictionary, length {len(self.client_hash_mapping)}")
            self.logger.info(f"Number of clients: {self.num_clients}")

            if self.head_id == get_client_id:
                self.switch_Status = True

        except Exception as e:
            self.logger.error(f"Error in handle_client_disconnected: {e}")

    def handle_client_data(self, json_data, cluster_id):
        try:
            client_id = json_data['client_id']
            model_hash = json_data['model_hash']
            self.client_hash_mapping[client_id] = model_hash
            self.logger.info(f"Model hash {model_hash} received from {client_id}")

            self.round += 1

            if len(self.client_hash_mapping) == self.num_clients:
                self.logger.info("Received model hashes from all clients in the cluster.")
                self.get_all_hash()

        except Exception as e:
            self.logger.error(f"Error in handle_client_data: {e}")


    def is_worker_head(self, client):
        try:
            if self.worker_head_node:
                return client

        except Exception as e:
            self.logger.error(f"Error in is_worker_head: {e}")
            return None

    def receive_internal_messages(self):
        try:
            self.client.on_message = self.on_message

        except Exception as e:
            self.logger.error(f"Error in receive_internal_messages: {e}")


    def stop_receiving_messages(self):
        try:
            self.client.unsubscribe(self.internal_cluster_topic)

        except Exception as e:
            self.logger.error(f"Error in stop_receiving_messages: {e}")

    def get_all_hash(self):
        try:
            while len(self.client_hash_mapping) != self.num_clients - 1:
                self.logger.debug("Waiting for all hashes to be available")
                time.sleep(4)

                if self.terimate_status:
                    self.logger.warning("Force to disconnect")
                    break

            self.logger.info("Extracting all hashes")
            hashes = list(self.client_hash_mapping.values())
            return hashes

        except Exception as e:
            self.logger.error(f"Error in get_all_hash: {e}")
            return None

    def global_model(self):
        try:
            if self.worker_head_node:
                return self.global_model_hash

            start_time = time.time()
            while not self.global_model_hash:
                self.logger.debug("Waiting for global model")
                time.sleep(2)
                elapsed_time = time.time() - start_time

                self.logger.warning(f"Trying to fetch global attempt: {int(elapsed_time)} seconds")

                if elapsed_time >= 6:
                    self.logger.warning("Timeout: Unable to get global model within 6 seconds")
                    return None

            return self.global_model_hash

        except Exception as e:
            self.logger.error(f"Error in global_model: {e}")
            return None

    
    # def send_id(self,role,id):
    #     message={
    #         "id":id,
    #         "role":role,
    #     }
    #     data=json.dumps(message)
    #     self.logger.info(data)
    #     if role=="User":
    #         self.client.publish(self.client_to_admin_topic,data,qos=1)
    #     elif role=="Admin":
    #         self.client.publish(self.admin_to_client_topic,data,qos=1)

    #     self.logger.debug(f"Successfully sent id:{str(id)} ")



    def send_client_to_admin_model(self, message):
        try:
            self.logger.info(f"send_client_to_admin_model: {message}")
            self.client.publish(self.client_to_admin_topic, message, qos=1)

        except Exception as e:
            self.logger.error(f"Error in send_client_to_admin_model: {e}")

    def send_client_to_admin_messages(self, message_json):
        try:
            self.client.publish(self.client_to_admin_topic, message_json, qos=1)

        except Exception as e:
            self.logger.error(f"Error in send_client_to_admin_messages: {e}")

    def send_admin_to_client_global_model(self, modelhash):
        try:
            self.logger.info(f" trying to Global model to internal_messages_model: {modelhash} ")
            data = json.dumps({"global_model": modelhash})
            self.client.publish(self.admin_to_client_topic, data, qos=1)
            self.logger.info("Successfully send Global model to internal_messages_model")

        except Exception as e:
            self.logger.error(f"Error in send_admin_to_client_global_model: {e}")

    
    def switch_head(self):
        try:
            if self.switch_Status:
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"Error in switch_head: {e}")
            return None

    def on_publish(self, client, userdata, mid):
        try:
            self.mid = mid
            self.logger.debug(f"Message Ack Published for client id: {client._client_id.decode('utf-8')} and (mid={self.mid})")

        except Exception as e:
            self.logger.error(f"Error in on_publish: {e}")
    def on_subscribe(self, client, userdata, mid, granted_qos):
        try:
            self.logger.debug(f"Message Ack Subscribe for client id: {client._client_id.decode('utf-8')} and (mid={mid})")

        except Exception as e:
            self.logger.error(f"Error in on_subscribe: {e}")

    def get_head_node_id(self):
        try:
            if self.worker_head_node:
                return self.head_id

        except Exception as e:
            self.logger.error(f"Error in get_head_node_id: {e}")
            return None

    def set_head_node_id(self, data):
        try:
            self.head_id = data['head_id']
            self.logger.info(f"set successful head id: {self.head_id}")
            time.sleep(6)

        except Exception as e:
            self.logger.error(f"Error in set_head_node_id: {e}")

    def generate_random_characters(self, length):
        try:
            return ''.join(random.choice('0123456789') for _ in range(length))

        except Exception as e:
            self.logger.error(f"Error in generate_random_characters: {e}")
            return None


    def switch_broker(self, new_broker_address):
        try:
            self.client.loop_stop()
            self.client.disconnect()

            self.broker_address = new_broker_address

            self.logger.info(f"New broker address : {new_broker_address}")

            self.connect_clients()
            self.logger.info(f"Successfully Switch : {new_broker_address}")

        except Exception as e:
            self.logger.error(f"Error in switch_broker: {e}")
    

if __name__ == "__main__":
    # Instantiate an MQTT cluster
    cluster = MQTTCluster("mqtt.broker.com", 5, "MyCluster", "global_topic", "internal_topic", True, 1)

    # Create and connect MQTT clients
    cluster.connect_clients()

    # Subscribe to internal messages
    cluster.receive_internal_messages()
