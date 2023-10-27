import paho.mqtt.client as mqtt
import random
import time
import json
import logging
# clients = []
class MQTTCluster:
    def __init__(self, broker_address, num_clients, cluster_name,inter_cluster_topic,internal_cluster_topic,head_status):
        self.broker_address = broker_address
        self.num_clients = num_clients
        
        self.cluster_name = cluster_name
        self.worker_head_node = head_status
        self.round = 0
        self.inter_cluster_topic=inter_cluster_topic
        self.internal_cluster_topic=internal_cluster_topic
        self.glb_msg=list()
        self.client=None
        self.global_model_hash=None
    

    def create_clients(self,client_num):
        self.client = mqtt.Client(f"{self.cluster_name}_Client_{client_num}")
        self.client.connected_flag = False
        self.client.bad_conn_flag = False

        self.client.on_connect=self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect=self.on_disconnect
        self.client.on_log=self._on_log


        self.client.connect(self.broker_address, 1883)
        self.client.subscribe(self.inter_cluster_topic, qos=1)
        self.client.subscribe(self.internal_cluster_topic, qos=1)
        # Set the "last will" message for client disconnection
        self.client.will_set("status/disconnect", "Client has disconnected", qos=1, retain=True)

        self.client.loop_start()
        # clients.append(client)

    def _on_log(self, client, userdata, level, buf):
        logging.info("mqtt log {}, client id {}.".format(buf, self.mqtt_connection_id))

    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected to broker")
            client.connected_flag = True
        # get worker head
        else:
            print(f"Connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        # if rc != 0:
        #     print(f"Unexpected disconnection with code {rc}")
        # else:
        #     print("Disconnected from MQTT broker")
        # Inform other clients about the disconnection
        print("Disconnected from MQTT broker")
        client.publish("status/disconnect", "Client has disconnected", qos=1, retain=True)



    def on_message(self, client, userdata, message):
        client_id = client._client_id.decode('utf-8')
        cluster_id = self.cluster_name


        # print(f"Received message: {message.payload.decode('utf-8')}")

        print("Topic: {}".format(self.internal_cluster_topic))


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
            # To Receive to head Only
                print(f"Received  Internal message in {cluster_id} from {client_id} as \n : {data} ")
                model_hash=data

                self.glb_msg.append({model_hash})
                print("model hash",self.glb_msg)
                print("length",len(self.glb_msg))

                time.sleep(2)
                
                if len(self.glb_msg)==2:
                    print("Got all train message from client in cluster ")
                    print("model hash",self.glb_msg)

                    self.send_model_hash()
                    # self.glb_msg.clear()

                    time.sleep(5)



                                 

        elif message.topic == self.inter_cluster_topic:
            data=message.payload.decode('utf-8')
            if self.is_worker_head(client):
                print(f"Inter-cluster message in {cluster_id} from {client_id} \n : {data}")
                time.sleep(5)

        
    def is_worker_head(self, client):

        if self.worker_head_node :
             return client
             


            
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

    def global_model(self):
         
        if self.global_model_hash:
            return self.global_model_hash
        else :
            print("No global model hashs")
         
         
    # def get_global_model_hash(self):
    #      return hash
    def receive_global_model_on_message(self):
         
         pass



    # Send Inter-cluster
    def send_inter_cluster_message(self, message):
        self.worker_head_node.publish(self.inter_cluster_topic, message)

    # Send 
    def send_internal_messages(self):
        # for client in client:
            # if client != self.worker_head_node:
                self.client.publish(self.internal_cluster_topic, f" Here is  in {self.cluster_name} from {client._client_id.decode('utf-8')} is training")
    
    def send_internal_messages_global_model(self,modelhash):
        print(" trying to Global model to internal_messages_model : ",modelhash)
        if self.is_worker_head(self.client):
            self.client.publish(self.internal_cluster_topic, f"global_model {modelhash}")
            print("Successfully send Global model to internal_messages_model  ")

    def send_internal_messages_model(self,modelhash):
        print("send_internal_messages_model : ",modelhash)

        print("Internal topic",self.internal_cluster_topic)    
        self.client.publish(self.internal_cluster_topic, f"{modelhash}")
        print("Successfully send_internal_messages_model  ")


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

