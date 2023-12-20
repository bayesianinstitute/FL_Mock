import paho.mqtt.client as mqtt
import json
import queue
from core.Logs_System.logger import Logger
from core.API.endpoint import *
from core.Role.MsgType import *

class MQTTCluster:
    def __init__(self,ip, broker_address,  internal_cluster_topic,  role):
        self.ip=ip
        self.logger=Logger(name='MqttComm_logger',api_endpoint=f"{self.ip}:8000/{update_logs}").get_logger()
        self.broker_address = broker_address
        self.internal_cluster_topic = internal_cluster_topic
        self.client = None
        # Generate a random UUID using a secure random number generator
        self.id = f"{role}_IP:{self.ip}"
        self.terimate_status = False
        self.received_admin_data_queue = queue.Queue()
        self.received_user_data_queue=queue.Queue()
        self.last_received_user_data = None


    def on_connect(self,client, userdata, flags, rc):
        self.logger.info(f"Connected to broker Successfully with result code {rc}")
        self.client.subscribe(self.internal_cluster_topic,qos=2) 

    def connect_clients(self,role,receiver):
        self.client = mqtt.Client(self.id)
        self.client.on_connect = self.on_connect

        self.client.on_message = self.on_message
        self.client.on_publish=self.on_publish
        will_set_msg=json.dumps({
                    "receiver": receiver,
                    "role": role,
                    "msg": "SendNetworkStatus",
                    "node_id": self.id,
                    "network_status": "disconnected"})
        
        self.client.will_set(self.internal_cluster_topic,will_set_msg , qos=2,)
        self.client.connect(self.broker_address, 1883)
        self.client.loop_start()

    def on_message(self, client, userdata, message):

        if message.topic == self.internal_cluster_topic:
            self.handle_internal_message(message,client)



    def handle_internal_message(self, message,client):
        data = message.payload.decode('utf-8')
        self.logger.critical(f"Received data: {data}")

        try:
            json_data = json.loads(data)

            if json_data.get("receiver") == 'Admin':
                self.logger.warning("The receiver is an admin.")
                self.received_admin_data_queue.put(data)

            elif json_data.get("receiver") == 'User' :
                nodeId=json_data.get("node_id") 
                msg_type = json_data.get("msg")

                if msg_type==SEND_GLOBAL_MODEL_HASH:
                    self.received_user_data_queue.put(data)
                    return

                self.logger.warning(f"Node with ID {nodeId} and your id {self.id}")
                
                if self.id==nodeId:
                    self.logger.critical("The receiver is User")
                    if self.received_user_data_queue.empty():
                        self.received_user_data_queue.put(data)

                    else:
                        last_element = self.received_user_data_queue.queue[-1]

                        if last_element != data:
                            self.received_user_data_queue.put(self.received_user_data_queue)

                            self.logger.warning("Last value put is the different as the front element.")

                        else:
                            self.logger.info("Last value put is the same as the front element.")
            
        except json.JSONDecodeError as e:
            pass  

    def handle_admin_data(self):
        try:
            return self.received_admin_data_queue.get_nowait()
        except queue.Empty:
            return None
        

    def handle_user_data(self,):
        
        try:
            return self.received_user_data_queue.get_nowait()
        except queue.Empty:
            return None


    def terimate_connection(self):
        try:
                self.client.disconnect()
                self.client.loop_stop()
                self.logger.warning("Disconnected from the MQTT broker.")
        except Exception as e:
            self.logger.error(f"Error during disconnection: {str(e)}")

    def handle_terminate_message(self, client_id, cluster_id):
        self.logger.warning(f"Received terminate message from {client_id} in cluster {cluster_id}")

        self.terimate_status= True
        

        self.logger.warning(f"ALL Should Disconnected message from client : {client_id}")
    
    def send_terminate_message(self, t_msg):
        message = {
            "client_id": self.id,
            "terimate_msg": t_msg
        }
        data = json.dumps(message)

        self.client.publish(self.internal_cluster_topic, data,qos=2)
        self.logger.info("Successfully sent send_terminate_message")

        return True    
    
    def send_internal_messages(self,message_json):

        self.client.publish(self.internal_cluster_topic,message_json)

    def on_publish(self,client, userdata, mid):
        self.logger.debug(f"Message Ack Published for client id : {client._client_id.decode('utf-8')} and  (mid={mid})")

    def on_subscribe(self,client, userdata, mid,granted_qos):
        self.logger.debug(f"Message Ack Subscribe for client id : {client._client_id.decode('utf-8')} and (mid={mid})")


    def switch_broker(self, new_broker_address):
        
        self.client.loop_stop()    
        self.client.disconnect()

        self.broker_address = new_broker_address

        self.logger.info(f"New broker address : {new_broker_address}")

        self.connect_clients()
        self.logger.info(f"Successfully Switch : {new_broker_address}")
    

if __name__ == "__main__":
    cluster = MQTTCluster("mqtt.broker.com", 5, "MyCluster", "global_topic", "internal_topic", True, 1)

    cluster.connect_clients()