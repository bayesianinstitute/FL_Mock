from core.API.endpoint import *
from core.Role.MsgType import *

import json

from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
import time
class Admin:
    def __init__(self, training_type, optimizer):
        self.apiClient=ApiClient()
        self.ml_operations = MLOperations(training_type, optimizer)

        self.logger = Logger(name='admin-role').get_logger()

        self.model_list = []

    def admin_logic(self,  mqtt_obj,id):
        try:
            self.is_admin = True
            self.logger.info("I am Admin ")

            while True:
                received_message = mqtt_obj.handle_admin_data()

                if received_message:
                  
                    self.logger.debug(f"incoming received message:   {received_message}")
                   


                    self.process_received_message(received_message,mqtt_obj)   

                time.sleep(1) 
                self.handle_node_operation(mqtt_obj)
             
    
        except Exception as e:
            self.logger.error(f"Error in admin_logic: {str(e)}")

    def get_operation_status(self, data):
        try:
            response = self.apiClient.post_request(get_operation_status, data)

            if response and response.status_code == 200:
                self.logger.info(f"POST update_network_status Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                self.logger.error(f"POST Request Failed: {response.status_code, response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in add_admin: {str(e)}")
            return None
 
 
    def  handle_node_operation(self,mqtt_obj):
    
        node_id=67
        data={
            "node_id":67,
        }
        operation=self.get_operation_status(data)
        operation_status = operation.get('operation_status')
        self.logger.warning(f"{operation_status} operation")

        
        if operation_status == 'terminate':
                self.handle_terminate_api(node_id,mqtt_obj)
        elif operation_status == 'pause':
                self.handle_pause_api(node_id,mqtt_obj)
        elif operation_status == 'resume':
                self.handle_resume_api(node_id,mqtt_obj)
        
        time.sleep(1) 
        


 
    def process_received_message(self, message,mqtt_obj):
        try:
            message_data = json.loads(message)
            msg_type = message_data.get("msg")
            role = message_data.get("role")
            node_id = message_data.get("node_id")
            training_status = message_data.get("training_status")
            network_status = message_data.get("network_status")
            accuracy = message_data.get("accuracy")
           
            loss = message_data.get("loss")
            model_hash = message_data.get("model_hash")
            
            if msg_type == SEND_NETWORK_STATUS:
                self.handle_network_status(node_id,role, network_status)                
            elif msg_type == SEND_TRAINING_STATUS:
                self.handle_training_status(node_id,role, training_status)
            elif msg_type == RECEIVE_MODEL_INFO:
                self.handle_receive_model_info(node_id, accuracy,loss,model_hash)





        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON message: {str(e)}")

    def handle_network_status(self, node_id,role, network_status):        
        data = {
            "role": role,
            "node_id": node_id,
            "network_status": network_status,
        }

        status = self.update_network_status(data)
        if status:
            self.logger.critical(f"Network status updated")
        else:
            self.logger.error("Network status not updated")
            
    def handle_training_status(self, node_id,role, training_status):
        data = {
            "role": role,
            "node_id": node_id,
            "training_status": training_status,
        }

        status = self.update_training_status(data)
        if status:
            self.logger.critical(f"Training status updated")
        else:
            self.logger.error("Training status not updated")

    # def handle_train_model(self, user_id, message_data,mqtt_obj):
    #     # Handle train model logic
    #     # Update database with model training information
    #     # self.db.add_model_training_info(user_id, message_data)
    #     # self.logger.info(f"Received model training info from user {user_id}: {message_data}")

    #     # # Check if global model is sent
    #     # if self.db.check_global_model_received(mq):
    #         # Aggregate and send global model through MQTT
    #         # global_model = self.db.aggregate_global_model()
    #         message_data=self.send_global_model(hash='QmbWLHYpFhvbD1BB67TfbHisesuq5VutDC5LYEGTxpgATB')
    #         mqtt_obj.send_internal_messages(message_data)
    #         self.logger.info("Sent global model to users")

    def handle_receive_model_info(self,node_id, accuracy,loss,model_hash):
        data = {
            "training_info":1,
            "node_id": node_id,
            "accuracy": accuracy,
            "loss":loss,
            "model_hash":model_hash,
        }
        status = self.update_receive_model_info(data)
        if status:
            self.logger.critical(f"Received Model Information")
        else:
            self.logger.error("Not Received Model Information")

    def handle_terminate_api(self, user_id,mqtt_obj):
        message_json = json.dumps({
                "receiver": 'User',
                "role": 'Admin',
                "node_id": user_id,
                "msg": TERMINATE_API,
            })
    
        
        self.logger.info(f"Terminated API for user {user_id}")
        mqtt_obj.send_internal_messages(message_json)

    def handle_pause_api(self, user_id,mqtt_obj):

        message_json = json.dumps({
        "receiver": 'User',
        "role": 'Admin',
        "node_id": user_id,
        "msg": PAUSE_API,
       })
        self.logger.info(f"Paused API for user {user_id}")

        mqtt_obj.send_internal_messages(message_json)



    def handle_resume_api(self, user_id,mqtt_obj):
        self.logger.info(f"Inside Handle Resume API")
        message_json = json.dumps({
        "receiver": 'User',
        "role": 'Admin',
        "node_id": user_id,
        "msg": RESUME_API,
       })
        self.logger.info(f"Resume API for user {user_id}")
        mqtt_obj.send_internal_messages(message_json)


    def send_global_model(hash='QmbWLHYpFhvbD1BB67TfbHisesuq5VutDC5LYEGTxpgATB'):
        message_json = json.dumps({
            "receiver": 'User',
            "msg": SEND_GLOBAL_MODEL_HASH,
            "Admin": 1,
            "global_hash":hash

        })
        return message_json


    def update_network_status(self, data):
        try:
            response = self.apiClient.post_request(create_or_update_status, data)

            if response and response.status_code == 201:
                self.logger.info(f"POST update_network_status Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                self.logger.error(f"POST Request Failed: {response.status_code, response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in add_admin: {str(e)}")
            return None
    
    def update_training_status(self, data):
        try:
            response = self.apiClient.post_request(create_or_update_status, data)

            if response and response.status_code == 201:
                self.logger.info(f"POST update_training_status Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                self.logger.error(f"POST Request Failed: {response.status_code, response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in add_admin: {str(e)}")
            return None
    
    def update_receive_model_info(self, data):
        try:
            response = self.apiClient.post_request(add_training_result, data)

            if response and response.status_code == 201:
                self.logger.info(f"POST update_receive_model_info Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                self.logger.error(f"POST Request Failed: {response.status_code, response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in add_admin: {str(e)}")
            return None    
        
    def handle_Disconnect_node_api(self,node_id):
        self.logger.warning(f"Disconnected {node_id}")
        pass
    
