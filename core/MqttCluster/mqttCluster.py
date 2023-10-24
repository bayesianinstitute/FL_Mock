import paho.mqtt.client as mqtt
import random
import time
import json
# clients = []
class MQTTCluster:
    def __init__(self, broker_address, num_clients, cluster_name,inter_cluster_topic,internal_cluster_topic):
        self.broker_address = broker_address
        self.num_clients = num_clients
        
        self.cluster_name = cluster_name
        self.worker_head_node = None
        self.round = 0
        self.inter_cluster_topic=inter_cluster_topic
        self.internal_cluster_topic=internal_cluster_topic
        self.glb_msg=list()
        self.client=None
    

    def create_clients(self,client_num):
        self.client = mqtt.Client(f"{self.cluster_name}_Client_{client_num}")
        self.client.connect(self.broker_address, 1883)
        self.client.subscribe(self.inter_cluster_topic, qos=0)
        self.client.subscribe(self.internal_cluster_topic, qos=0)
        self.client.on_message = self.on_message
        self.client.loop_start()
        # clients.append(client)


            
    def subscribe_to_internal_messages(self):
        # Subscribe to the internal_cluster_topic for message reception
        # for client in self.client:
            # if client != self.worker_head_node:
                self.client.subscribe(self.internal_cluster_topic, qos=0)

    def receive_internal_messages(self):
        # for client in self.client:
            # if client != self.worker_head_node:
                self.client.on_message = self.on_message

    def stop_receiving_messages(self):
        # for client in self.client:
            # if client != self.worker_head_node:
                self.client.unsubscribe(self.internal_cluster_topic)

    def send_model_hash(self, ):
          if len(self.glb_msg)==2:
                return self.glb_msg
          else :
                return False

    def on_message(self, client, userdata, message):
        client_id = client._client_id.decode('utf-8')
        cluster_id = self.cluster_name


        print(f"Received message: {message.payload.decode('utf-8')}")

        print("Topic: {}".format(self.internal_cluster_topic))


        if message.topic == self.internal_cluster_topic:
            

            # if self.is_worker_head(client):
            # To Receive to head Only
                print(f"Received  Internal message in {cluster_id} from {client_id} as \n : {message.payload.decode('utf-8')} ")
                model_hash=message.payload.decode('utf-8')

                self.glb_msg.append({model_hash})
                print("model hash",self.glb_msg)
                print("length",len(self.glb_msg))

                time.sleep(2)
                
                if len(self.glb_msg)==2:
                    print("Got all train message from client in cluster ")
                    print("model hash",self.glb_msg)




                    time.sleep(5)
                    receive=0                
        elif message.topic == self.inter_cluster_topic:
            data=message.payload.decode('utf-8')
            if self.is_worker_head(client):
                print(f"Inter-cluster message in {cluster_id} from {client_id} \n : {data}")
                time.sleep(5)

    # Send Inter-cluster
    def send_inter_cluster_message(self, message):
        self.worker_head_node.publish(self.inter_cluster_topic, message)

    # Send 
    def send_internal_messages(self):
        # for client in client:
            # if client != self.worker_head_node:
                self.client.publish(self.internal_cluster_topic, f" Here is  in {self.cluster_name} from {client._client_id.decode('utf-8')} is training")
    
    def send_internal_messages_model(self,modelhash):
        print("send_internal_messages_model : ",modelhash)

        print("Internal topic",self.internal_cluster_topic)    
        self.client.publish(self.internal_cluster_topic, f"{modelhash}")
        print("Successfully send_internal_messages_model  ")

    # get worker head
    def is_worker_head(self, client):
        return client == self.worker_head_node



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
        self.switch_worker_head_node()
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

        #         # send Agregated message in inter-Cluster
        #         if len(self.glb_msg)>=len(clients)-1:
        #             self.aggratedglobalMsg()
        #             time.sleep(6)
        #             pass

        #         # Send internal messages
                # self.send_internal_messages()
        #         time.sleep(5)
        #         self.round += 1
        #         print("Round completed:", self.round)

        #         if self.round == 10:
        #             print("All Rounds completed!")

        #         time.sleep(5)  # Sleep for 5 seconds between rounds

        except KeyboardInterrupt:
            for client in self.client:
                client.loop_stop()
                client.disconnect()