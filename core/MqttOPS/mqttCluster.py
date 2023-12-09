import paho.mqtt.client as mqtt
import random
import time
import json
import queue
from core.Logs_System.logger import Logger


class MQTTCluster:
    def __init__(self, broker_address, num_clients, cluster_name,  internal_cluster_topic, head_status, id):
        self.logger=Logger(name='MqttComm_logger').get_logger()
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
        self.id = f"{self.cluster_name}_Client_{id}"
        self.terimate_status = False
        self.head_id=None
        self.switch_Status=False
        self.received_data_queue = queue.Queue()


    def on_connect(self,client, userdata, flags, rc):
        self.logger.warning(f"Connected with result code {rc}")
        self.client.subscribe(self.internal_cluster_topic,qos=2) 

    def connect_clients(self):
        self.client = mqtt.Client(self.id)
        self.client.on_connect = self.on_connect

        self.client.on_message = self.on_message
        self.client.on_publish=self.on_publish
        # self.client.on_subscribe=self.on_subscribe
        will_set_msg=json.dumps({"Client-disconnected": self.id})
        self.client.will_set(self.internal_cluster_topic,will_set_msg , qos=2,)
        self.client.connect(self.broker_address, 1883)
        # self.client.subscribe(self.internal_cluster_topic, qos=2)
        self.client.loop_start()

    def get_head_node_id(self):
        if self.worker_head_node:
            return self.head_id

    def set_head_node_id(self,data):
        self.head_id=data['head_id']
        self.logger.info(f"set successful head id: {self.head_id}")


    def on_message(self, client, userdata, message):
        client_id = client._client_id.decode('utf-8')
        cluster_id = self.cluster_name

        if message.topic == self.internal_cluster_topic:
            self.handle_internal_message(message, client_id, cluster_id,client)



    def handle_internal_message(self, message, client_id, cluster_id,client):
        data = message.payload.decode('utf-8')
        self.logger.critical(f"Received data: {data}")

        try:
            json_data = json.loads(data)


            # Check if the receiver is admin
            if json_data.get("receiver") == 'Admin':
                self.logger.critical("The receiver is an admin.")
                self.received_data_queue.put(json_data)

                # This is in mqtt.py file and   Need to transfer json data to admin.py file
            elif json_data.get("receiver") == 'User' :
                self.logger.critical("The receiver is User")
                self.received_data_queue.put(json_data)



            # if "head_id" in json_data:
            #     self.set_head_node_id(json_data)

            # if 'global_model' in json_data:
            #     self.handle_global_model(json_data, client_id, cluster_id)

            # if self.is_worker_head(client):
            #     self.handle_internal_data(json_data, client_id, cluster_id)
            
            # # Check for the terminate message
            # if 'terimate_msg' in json_data:
            #     self.handle_terminate_message(client_id, cluster_id)

        except json.JSONDecodeError as e:
            pass  # Handle JSON decoding errors

    def handle_admin_data(self):
        try:
            return self.received_data_queue.get_nowait()
        except queue.Empty:
            return None
    def handle_user_data(self,):
        
        try:
            return self.received_data_queue.get_nowait()
        except queue.Empty:
            return None


    def terimate_status(self):
        return self.terimate_status

    def handle_terminate_message(self, client_id, cluster_id):
    # Handle the termination message here
        self.logger.warning(f"Received terminate message from {client_id} in cluster {cluster_id}")

        self.terimate_status= True
        

        self.logger.warning(f"ALL Should Disconnected message from client : {client_id}")
    
    # Send the termination message
    def send_terminate_message(self, t_msg):
        message = {
            "client_id": self.id,
            "terimate_msg": t_msg
        }
        data = json.dumps(message)

        self.client.publish(self.internal_cluster_topic, data,qos=2)
        self.logger.info("Successfully sent send_terminate_message")

        return True    


    def handle_global_model(self, json_data, client_id, cluster_id):
        extract = json_data['global_model']

        self.logger.info(f"Received Global message in {cluster_id} from {client_id} as:\n{extract}")

        # Need api to add Global model hash in database
        self.global_model_hash = extract

    def handle_internal_data(self, json_data, client_id, cluster_id):
        try : 
            if 'Client-disconnected' in json_data:
                self.handle_client_disconnected(json_data)

            if 'client_id' in json_data:
                self.handle_client_data(json_data, cluster_id)
            if 'msg' in json_data:
                self.handle_client_msg(json_data)
        except :
            self.logger.error("exception in handle_internal_data ")

    def handle_client_msg(self,json_data):
        self.logger.info(json_data['msg'])

    def handle_client_disconnected(self, json_data):
        # TODO: need admin api put to update number of client in database and status
        try :
            get_client_id = json_data['Client-disconnected']
            self.logger.warning(f"Disconnected node id : {get_client_id}" )
            self.num_clients -= 1
            self.logger.info(f"Remove client from dictionary, length {len(self.client_hash_mapping)}")
            self.logger.info(f"Number of clients: {self.num_clients}" )
            if self.head_id==get_client_id:
                self.switch_Status=True
        except :
            self.logger.error("exception in handle_client_disconnected ")

    def handle_client_data(self, json_data, cluster_id):
        try:
            client_id = json_data['client_id']
            model_hash = json_data['model_hash']
            self.client_hash_mapping[client_id] = model_hash
            self.logger.info(f"Model hash {model_hash} received from {client_id} ")

            self.round += 1

            if len(self.client_hash_mapping) == self.num_clients:
                self.logger.info("Received model hashes from all clients in the cluster.")
                self.get_all_hash()
        except :
            self.logger.error("exception in handle_client_data ")


    def is_worker_head(self, client):
        if self.worker_head_node:
            return client

    def subscribe_to_internal_messages(self):
        # Subscribe to the internal_cluster_topic for message reception
        self.client.subscribe(self.internal_cluster_topic, qos=2)

    def receive_internal_messages(self):
        self.client.on_message = self.on_message

    def stop_receiving_messages(self):
        self.client.unsubscribe(self.internal_cluster_topic)

    # 
    def get_all_hash(self):
        while len(self.client_hash_mapping) != self.num_clients-1:
            # Wait for all hashes to be available
            self.logger.debug("Waiting for all hashes to be available")
            time.sleep(4)
            if self.terimate_status:
                self.logger.warning("Force to disconnect")
                break
            pass

        # Once all hashes are available, extract and return them
        self.logger.info("Extracting all hashes")
        hashes = list(self.client_hash_mapping.values())
        return hashes


    def global_model(self):
        if self.worker_head_node:
            return self.global_model_hash

        start_time = time.time()
        while not self.global_model_hash:
            # You can add a sleep here to reduce CPU usage
            self.logger.debug("Waiting for global model")

            time.sleep(2)
            elapsed_time = time.time() - start_time

            self.logger.warning(f"Trying to fetch global attempt: {int(elapsed_time)} seconds")


            if elapsed_time >= 6:
                self.logger.warning(f"Timeout: Unable to get global model within 6 seconds")
                return None

        return self.global_model_hash

    
    def send_head_id(self,id):
        message={
            "head_id":id,
        }
        data=json.dumps(message)
        self.logger.info(data)
        self.client.publish(self.internal_cluster_topic,data,qos=2)
        self.logger.info(f"Successfully Head id:{str(id)} ")



    def send_internal_messages_model(self, message):

        self.logger.info(f"send_internal_messages_model:{message}" )
        self.client.publish(self.internal_cluster_topic, message,qos=2)
        self.logger.info("Successfully sent_internal_messages_model")


    def send_internal_messages(self,message_json):

        self.client.publish(self.internal_cluster_topic,message_json)
        # self.logger.info(f" topic : {self.internal_cluster_topic} Here is in {self.cluster_name} from {client._client_id.decode('utf-8')} is training")

    def send_internal_messages_global_model(self, modelhash):
        self.logger.info(f" trying to Global model to internal_messages_model: {modelhash} " )
        if self.is_worker_head(self.client):
            data = json.dumps({"global_model": modelhash})
            self.client.publish(self.internal_cluster_topic, data,qos=2)
            self.logger.info("Successfully send Global model to internal_messages_model")
    
    def switch_head(self, ):

        if self.switch_Status:
            return True
        else : 
            return False

    def on_publish(self,client, userdata, mid):
        self.logger.debug(f"Message Ack Published for client id : {client._client_id.decode('utf-8')} and  (mid={mid})")

    def on_subscribe(self,client, userdata, mid,granted_qos):
        self.logger.debug(f"Message Ack Subscribe for client id : {client._client_id.decode('utf-8')} and (mid={mid})")



    def switch_broker(self, new_broker_address):
        # Disconnect existing clients
        
        self.client.loop_stop()    
        self.client.disconnect()

        # Update the broker address
        self.broker_address = new_broker_address

        self.logger.info(f"New broker address : {new_broker_address}")

        # Re-create clients with the new broker address
        self.connect_clients()
        self.logger.info(f"Successfully Switch : {new_broker_address}")
    

if __name__ == "__main__":
    # Instantiate an MQTT cluster
    cluster = MQTTCluster("mqtt.broker.com", 5, "MyCluster", "global_topic", "internal_topic", True, 1)

    # Create and connect MQTT clients
    cluster.connect_clients()

    # Subscribe to internal messages
    cluster.subscribe_to_internal_messages()