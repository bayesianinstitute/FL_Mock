import json
from core.API.endpoint import *
from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
from core.MqttOPS.mqtt_operations import MqttOperations

import json

class UserOPS:
    def __init__(self, training_type, optimizer,internal_cluster_topic, cluster_name,
                                              broker_service, min_node, is_admin, id):
        self.logger = Logger(name='user-role').get_logger()
        
        self.apiClient = ApiClient()
        self.ml_operations = MLOperations(training_type, optimizer)
        self.mqtt_operations = MqttOperations(internal_cluster_topic, cluster_name,
                                              broker_service, min_node, is_admin, id)
        
        self.mqtt_obj = self.mqtt_operations.start_dfl_using_mqtt()
        

    def user_logic(self, ):

        #TODO: Save Your User Data in database


        #TODO: Get User Data from database
        #TODO: Send User Data to Admin
        
        while(1):
            
            
            
            
            user_status = self.update_network_status()
            self.send_network_status( user_status)

            user_status = self.update_training_status()
            self.send_training_status(user_status)

            hash, accuracy, loss = self.ml_operations.train_machine_learning_model()
            self.logger.info(f"Model hash: {hash}")

            self.send_model_to_internal_cluster( user_status, hash, accuracy, loss)

            latest_global_model_hash = self.mqtt_obj.global_model()

            if latest_global_model_hash:
                self.process_global_model_hash( latest_global_model_hash)


    def update_network_status(self):
        connected_status = self.apiClient.put_request(network_connected_endpoint)

        if connected_status.status_code == 200:
            self.logger.info(f"PUT network_status Request Successful: {connected_status.text}")
            return json.loads(connected_status.text)
        else:
            self.logger.info(f"PUT Request Failed: {connected_status.status_code, connected_status.text}")
            return None

    def send_network_status(self,  user_status):
        if user_status:
            message_json = json.dumps({
                "msg": "connection_status",
                "id": user_status['id'],
                "network_status": user_status['network_status']
            })
            self.mqtt_obj.send_internal_messages(message_json)

    def update_training_status(self):
        training_status = self.apiClient.put_request(toggle_training_status_endpoint)

        if training_status.status_code == 200:
            self.logger.info(f"PUT training_status Request Successful: {training_status.text}")
            return json.loads(training_status.text)
        else:
            self.logger.error(f"PUT Request Failed: {training_status.status_code, training_status.text}")
            return None

    def send_training_status(self, user_status):
        if user_status:
            message_json = json.dumps({
                "msg": "training_status",
                "id": user_status['id'],
                "training_status": user_status['training_status'],
            })
            self.mqtt_obj.send_internal_messages(message_json)

    def send_model_to_internal_cluster(self,  user_status, hash, accuracy, loss):
        if user_status:
            message_json = json.dumps({
                "client_id": user_status['id'],
                "model_hash": hash,
                "accuracy": accuracy,
                "loss": loss,
            })
            self.mqtt_obj.send_internal_messages_model(message_json)

    def process_global_model_hash(self,  latest_global_model_hash):
        self.logger.info(f"I am not aggregator, got global model hash: {latest_global_model_hash}")
        self.ml_operations.is_global_model_hash(latest_global_model_hash)
        self.mqtt_obj.global_model_hash = None

