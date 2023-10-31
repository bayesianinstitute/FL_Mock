import paho.mqtt.client as mqtt
import random
import time
import json
import logging
# clients = []
class MQTTCluster:
    def __init__(self, broker_address, num_clients, cluster_name,global_cluster_topic,internal_cluster_topic,head_status,id):
        self.broker_address = broker_address
        self.num_clients = num_clients
        
        self.cluster_name = cluster_name
        self.worker_head_node = head_status
        self.round = 0
        self.global_cluster_topic=global_cluster_topic
        self.internal_cluster_topic=internal_cluster_topic
        self.client=None
        self.global_model_hash=None
        self.client_hash_mapping = {}
        self.round = 0
        self.id=f"{self.cluster_name}_Client_{id}"
    

    def create_clients(self):
        self.client = mqtt.Client(self.id)
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address, 1883)

        self.client.subscribe(self.global_cluster_topic, qos=1)
        self.client.subscribe(self.internal_cluster_topic, qos=1)

        self.client.loop_start()



    def on_message(self, client, userdata, message):
        client_id = client._client_id.decode('utf-8')
        print("cluster name " , self.cluster_name)
        cluster_id = self.cluster_name


        # print(f"Received message: {message.payload.decode('utf-8')}")

        print("Topic: {}".format(self.internal_cluster_topic))
        print("message topic : {} ".format(message.topic))
        print("worker_head_node : ",self.worker_head_node)

        print("This is the Worker_head : ",self.is_worker_head(client))


        if message.topic == self.internal_cluster_topic:

            data=message.payload.decode('utf-8')

            extract_global_message=data.find('global_model')

            string='global_model'
            # Check global_model
            if data.find(string)==0:
                lenght=len(string)+1
                extract=data[lenght:]
                if self.worker_head_node==False :
                    print(f"Received  Global message in {cluster_id} from {client_id} as \n : {extract} ")
                    self.global_model_hash=extract


                      
            if self.is_worker_head(client):
                print(f"Received Internal message in {cluster_id} from {client_id} as:\n{data}")
                get_data = json.loads(data)
                client_id = get_data["client_id"]
                model_hash = get_data["model_hash"]
                print("Received client_id:", client_id)
                print("Received model_hash:", model_hash)

                time.sleep(5)
                self.client_hash_mapping[client_id] = model_hash
                print("Model hash received from", client_id, "Round",self.round)
                self.round += 1
                print("client_hash_mapping",self.client_hash_mapping )

                print("num_clients is", self.num_clients)
                print("length ",len(self.client_hash_mapping))

                if len(self.client_hash_mapping) == self.num_clients:
                    print("Received model hashes from all clients in the cluster.")
                    self.send_model_hash()
                    time.sleep(5)



                                 

        elif message.topic == self.global_cluster_topic:
            data=message.payload.decode('utf-8')
            if self.is_worker_head(client):
                print(f"Inter-cluster message in {cluster_id} from {client_id} \n : {data}")
                time.sleep(5)

        
    def is_worker_head(self, client):

        if self.worker_head_node :
             return client
             


            
    def subscribe_to_internal_messages(self):
        # Subscribe to the internal_cluster_topic for message reception
                self.client.subscribe(self.internal_cluster_topic, qos=0)

    def receive_internal_messages(self):
                self.client.on_message = self.on_message

    def stop_receiving_messages(self):
                self.client.unsubscribe(self.internal_cluster_topic)

    def send_model_hash(self, ):

        if len(self.client_hash_mapping) == self.num_clients:  
          # Extract all hashes
          hashes = list(self.client_hash_mapping.values())
          return hashes
        else :
            return False

    def global_model(self):
         
        if self.global_model_hash:
            return self.global_model_hash
        else :
            print("No global model hashs")

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
            
         
    # Send Inter-cluster
    def send_inter_cluster_message(self, message):
        self.worker_head_node.publish(self.global_cluster_topic, message)

    # Send 
    def send_internal_messages(self):
        # for client in client:
            # if client != self.worker_head_node:
                self.client.publish(self.internal_cluster_topic, f" Here is  in {self.cluster_name} from {client._client_id.decode('utf-8')} is training")
                print(self.internal_cluster_topic, f" Here is  in {self.cluster_name} from {client._client_id.decode('utf-8')} is training")

    
    def send_internal_messages_global_model(self,modelhash):
        print(" trying to Global model to internal_messages_model : ",modelhash)
        if self.is_worker_head(self.client):
            self.client.publish(self.internal_cluster_topic, f"global_model {modelhash}")
            print("Successfully send Global model to internal_messages_model  ")


    def switch_broker(self, new_broker_address):
        # Disconnect existing clients
        for client in client:
            client.loop_stop()
            client.disconnect()

        # Update the broker address
        self.broker_address = new_broker_address

        # Re-create clients with the new broker address
        self.create_clients()
    

    def run(self):
        try:
            # pass
            print("")
        #     while self.round < 10:  # Run for a specified number of rounds

        #         # Switch broker after round 6
        #         if self.round == 6:
        #             new_broker_address = "broker.hivemq.com"  # Replace with your new broker address
        #             print(f"Switching broker to {new_broker_address} after round 6")
        #             self.switch_broker(new_broker_address)



        #         # Switch worker head node when the round is even
        #         if self.round % 2 == 0:
        #             print(f"Changing worker head in {self.cluster_name} !!!!!!!!!!!!!!!")
        #             self.switch_worker_head_node()
        #             print("New Head Node:", self.get_head_node())
        #             time.sleep(2)




        except KeyboardInterrupt:
            for client in self.client:
                client.loop_stop()
                client.disconnect()

