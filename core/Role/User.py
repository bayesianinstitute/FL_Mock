import json
from core.API.endpoint import *
from core.Role.MsgType import *

from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
class User:
    def __init__(self,training_type,optimizer):
        self.apiClient=ApiClient()
        self.ml_operations = MLOperations(training_type, optimizer)
        self.logger = Logger(name='user-role').get_logger()
        self.mqtt_obj=None
        
    def user_logic(self,mqtt_obj):
       
        try:
            while True:
                user_status = self.update_network_status()
                self.send_network_status(user_status,mqtt_obj)

                user_status = self.update_training_status()
                self.send_training_status(user_status,mqtt_obj)

                hash, accuracy, loss = self.ml_operations.train_machine_learning_model()
                self.logger.info(f"Model hash: {hash}")

                self.send_model_to_internal_cluster(user_status, hash, accuracy, loss,mqtt_obj)

                latest_global_model_hash = mqtt_obj.global_model()

                if latest_global_model_hash:
                    self.process_global_model_hash(latest_global_model_hash,mqtt_obj)

        except Exception as e:
            self.logger.error(f"Error in user_logic: {str(e)}")
        
        
    def update_network_status(self):
        try:
            connected_status = self.apiClient.put_request(network_connected_endpoint)

            if connected_status.status_code == 200:
                self.logger.info(f"PUT network_status Request Successful: {connected_status.text}")
                return json.loads(connected_status.text)
            else:
                self.logger.info(f"PUT Request Failed: {connected_status.status_code, connected_status.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error in update_network_status: {str(e)}")
            return None

    def send_network_status(self, user_status,mqtt_obj):
        try:
            if user_status:
                message_json = json.dumps({
                    "receiver": 'Admin',
                    "msg": SEND_NETWORK_STATUS,
                    "id": user_status['id'],
                    "network_status": user_status['network_status']
                })
                mqtt_obj.send_internal_messages(message_json)

        except Exception as e:
            self.logger.error(f"Error in send_network_status: {str(e)}")

    def update_training_status(self):
        try:
            training_status = self.apiClient.put_request(toggle_training_status_endpoint)

            if training_status.status_code == 200:
                self.logger.info(f"PUT training_status Request Successful: {training_status.text}")
                return json.loads(training_status.text)
            else:
                self.logger.error(f"PUT Request Failed: {training_status.status_code, training_status.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error in update_training_status: {str(e)}")
            return None

    def send_training_status(self, user_status,mqtt_obj):
        try:
            if user_status:
                message_json = json.dumps({
                    "receiver": 'Admin',
                    "msg": SEND_TRAINING_STATUS,
                    "id": user_status['id'],
                    "training_status": user_status['training_status'],
                })
                mqtt_obj.send_internal_messages(message_json)

        except Exception as e:
            self.logger.error(f"Error in send_training_status: {str(e)}")

    def send_model_to_internal_cluster(self, user_status, hash, accuracy, loss,mqtt_obj):
        
        try:
            if user_status:
                message_json = json.dumps({
                    "receiver": 'Admin',
                    "msg": RECEIVE_MODEL_INFO,

                    "client_id": user_status['id'],
                    "model_hash": hash,
                    "accuracy": accuracy,
                    "loss": loss,
                })
                mqtt_obj.send_internal_messages(message_json)

        except Exception as e:
            self.logger.error(f"Error in send_model_to_internal_cluster: {str(e)}")

    def process_global_model_hash(self, latest_global_model_hash,mqtt_obj):
        try:
            self.logger.info(f"I am not aggregator, got global model hash: {latest_global_model_hash}")
            self.ml_operations.is_global_model_hash(latest_global_model_hash)
            mqtt_obj.global_model_hash = None

        except Exception as e:
            self.logger.error(f"Error in process_global_model_hash: {str(e)}")