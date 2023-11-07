import paho.mqtt.client as mqtt
import random
import time
import json
import logging
# clients = []
class MQTTCluster:
    def __init__(self, broker_address, num_clients, cluster_name, global_cluster_topic, internal_cluster_topic, head_status, id):
        self.broker_address = broker_address
        self.num_clients = num_clients
        self.cluster_name = cluster_name
        self.worker_head_node = head_status
        self.round = 0
        self.global_cluster_topic = global_cluster_topic
        self.internal_cluster_topic = internal_cluster_topic
        self.client = None
        self.global_model_hash = None
        self.client_hash_mapping = {}
        self.round = 0
        self.id = f"{self.cluster_name}_Client_{id}"
        self.terimate_status = False

    def create_clients(self):
        self.client = mqtt.Client(self.id)
        self.client.on_message = self.on_message
        will_set_msg=json.dumps({"Client-disconnected": self.id})
        self.client.will_set(self.internal_cluster_topic,will_set_msg , qos=1,)
        self.client.connect(self.broker_address, 1883)
        self.client.subscribe(self.global_cluster_topic, qos=1)
        self.client.subscribe(self.internal_cluster_topic, qos=1)
        self.client.loop_start()


    def on_message(self, client, userdata, message):
        client_id = client._client_id.decode('utf-8')
        cluster_id = self.cluster_name

        if message.topic == self.internal_cluster_topic:
            self.handle_internal_message(message, client_id, cluster_id,client)
        elif message.topic == self.global_cluster_topic and self.is_worker_head(client):
            self.handle_global_message(message, client_id, cluster_id)

    def handle_internal_message(self, message, client_id, cluster_id,client):
        data = message.payload.decode('utf-8')
        try:
            json_data = json.loads(data)
         
            print("Received data: ",json_data)

            if 'global_model' in json_data:
                self.handle_global_model(json_data, client_id, cluster_id)

            if self.is_worker_head(client):
                self.handle_internal_data(json_data, client_id, cluster_id)
            
            # Check for the terminate message
            if 'terimate_msg' in json_data:
                self.handle_terminate_message(client_id, cluster_id)

        except json.JSONDecodeError as e:
            pass  # Handle JSON decoding errors

    def terimate_status(self):
        return self.terimate_status

    def handle_terminate_message(self, client_id, cluster_id):
    # Handle the termination message here
        print(f"Received terminate message from {client_id} in cluster {cluster_id}")

        self.terimate_status= True
        
        time.sleep(4)

        print(f"ALL Should Disconnected message from client : {client_id}")

    def handle_global_message(self, message, client_id, cluster_id):
        data = message.payload.decode('utf-8')
        try:
            message_data = json.loads(data)
            if "data" in message_data:
                message_content = message_data["data"]
                print(f"Inter-cluster message in {cluster_id} from {client_id}:\n{message_content}")
            else:
                print("No 'data' field in the global message.")
            time.sleep(5)

        except json.JSONDecodeError:
            print("Error decoding JSON message")

    def handle_global_model(self, json_data, client_id, cluster_id):
        extract = json_data['global_model']

        print(f"Received Global message in {cluster_id} from {client_id} as:\n{extract}")
        self.global_model_hash = extract

    def handle_internal_data(self, json_data, client_id, cluster_id):
        if 'Client-disconnected' in json_data:
            self.handle_client_disconnected(json_data)

        if 'client_id' in json_data:
            self.handle_client_data(json_data, cluster_id)

    def handle_client_disconnected(self, json_data):
        get_client_id = json_data['Client-disconnected']
        print("Disconnected node id", get_client_id)
        self.num_clients -= 1
        print("Remove client from dictionary, length", len(self.client_hash_mapping))
        print("Number of clients:", self.num_clients)
        time.sleep(5)

    def handle_client_data(self, json_data, cluster_id):
        client_id = json_data['client_id']
        model_hash = json_data['model_hash']
        self.client_hash_mapping[client_id] = model_hash
        print(f"Model hash {model_hash} received from {client_id} ")
        time.sleep(2)

        self.round += 1

        if len(self.client_hash_mapping) == self.num_clients:
            print("Received model hashes from all clients in the cluster.")
            self.send_model_hash()
            time.sleep(5)


    def is_worker_head(self, client):
        if self.worker_head_node:
            return client

    def subscribe_to_internal_messages(self):
        # Subscribe to the internal_cluster_topic for message reception

        self.client.subscribe(self.internal_cluster_topic, qos=0)

    def receive_internal_messages(self):
        self.client.on_message = self.on_message

    def stop_receiving_messages(self):
        self.client.unsubscribe(self.internal_cluster_topic)

    def get_all_model_hash(self):
        while len(self.client_hash_mapping) != self.num_clients:
            # Wait for all hashes to be available
            print("Waiting for all hashes to be available")
            time.sleep(4)
            if self.terimate_status:
                print("Force to disconnect")
                break
            pass

        # Once all hashes are available, extract and return them
        print("Extracting all hashes")
        hashes = list(self.client_hash_mapping.values())
        return hashes


    def global_model(self):

        if self.worker_head_node:
            
            return self.global_model_hash

        
        while not self.global_model_hash:
            # You can add a sleep here to reduce CPU usage
            print("Waiting for global model")

            time.sleep(5)  
            if self.terimate_status:
                print("Force to disconnect")
                break
            pass
        return self.global_model_hash


    def send_terimate_message(self, t_msg):
        message = {
            "client_id": self.id,
            "terimate_msg": t_msg
        }
        data = json.dumps(message)

        self.client.publish(self.internal_cluster_topic, data)
        print("Successfully sent send_terimate_message")

        return True        

    def send_internal_messages_model(self, modelhash):
        message = {
            "client_id": self.id,
            "model_hash": modelhash
        }
        data = json.dumps(message)
        print("send_internal_messages_model:", data)
        print("Internal topic", self.internal_cluster_topic)
        self.client.publish(self.internal_cluster_topic, data)
        print("Successfully sent_internal_messages_model")

    def send_inter_cluster_message(self, message):
        message_json = json.dumps({"data": message})
        self.worker_head_node.publish(self.global_cluster_topic, message_json)
        print("Successfully sent_inter_cluster_message")

    def send_internal_messages(self):
        # message_json = json.dumps({"data": message})
        self.client.publish(self.internal_cluster_topic, f" Here is in {self.cluster_name} from {client._client_id.decode('utf-8')} is training")
        print(self.internal_cluster_topic, f" Here is in {self.cluster_name} from {client._client_id.decode('utf-8')} is training")

    def send_internal_messages_global_model(self, modelhash):
        print(" trying to Global model to internal_messages_model: ", modelhash)
        if self.is_worker_head(self.client):
            data = json.dumps({"global_model": modelhash})
            self.client.publish(self.internal_cluster_topic, data)
            print("Successfully send Global model to internal_messages_model")
    
    def switch_head(self, ):
        
        pass


    def switch_broker(self, new_broker_address):
        # Disconnect existing clients
        
        self.client.loop_stop()    
        self.client.disconnect()

        # Update the broker address
        self.broker_address = new_broker_address

        print("New broker address : ",new_broker_address)

        # Re-create clients with the new broker address
        self.create_clients()
        print("Successfully Switch : ",new_broker_address)
    

if __name__ == "__main__":
    # Instantiate an MQTT cluster
    cluster = MQTTCluster("mqtt.broker.com", 5, "MyCluster", "global_topic", "internal_topic", True, 1)

    # Create and connect MQTT clients
    cluster.create_clients()

    # Subscribe to internal messages
    cluster.subscribe_to_internal_messages()

# Implement custom logic for handling messages
# Override the on_message method
