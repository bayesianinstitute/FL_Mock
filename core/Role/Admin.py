from core.API.endpoint import *
from core.Role.MsgType import *

import json

from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
# admin_module.py
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
                # Receive messages using MQTT
                received_message = mqtt_obj.handle_admin_data()

                if received_message:
                    # Process received messages
                    self.logger.debug(f"incoming received message:   {received_message}")
                    # mqtt_obj.current_data.clear()

                    self.process_received_message(received_message,mqtt_obj)   

                time.sleep(1) 
             
             
            # while(1):

            #     message_json = json.dumps({
            #         "msg": "AFAAN",
            #         "id": "user_status['id']",
            #         "network_status": "user_status['network_status']"
            #     })
            #     mqtt_obj.send_internal_messages(message_json)
            #     time.sleep(9)
            #     admin_data = {
            #         "training_status": "in_progress",
            #         "role": "Admin",
            #         "node_id": 8,
            #         "model_hash": "your_model_hash_here",
            #         "network_status": "connected"
            #     }

            #     status = self.add_admin(admin_data)
            #     if status:
            #         self.logger.info("Added")
            #     else:
            #         self.logger.error("Not Added")

            #     user_count = self.get_node_count()

            #     if user_count == 1:
            #         self.logger.debug("User count: 1")
            #         data = {
            #             "global_model_hash": "HAsha256",
            #         }

            #         status = self.add_global_model_hash(data)
            #         if status:
            #             self.logger.debug("Added global model")
            #         else:
            #             self.logger.error("Not Added global model")
            #     elif user_count > 2:
            #         self.logger.debug("More than User count: 2")
            #         data = {
            #             "global_model_hash": "HAsha256",
            #         }

            #         status = self.add_global_model_hash(data)
            #         if status:
            #             self.logger.debug("Added global model")
            #         else:
            #             self.logger.error("Not Added global model")

        except Exception as e:
            self.logger.error(f"Error in admin_logic: {str(e)}")
 
    def process_received_message(self, message,mqtt_obj):
        try:
            # Parse the received JSON message
            self.logger.warning(f"Received message length: {len(message)}")
            message_data = json.loads(message)

            # Extract relevant information from the message
            msg_type = message_data.get("msg")
            role = message_data.get("role")
            node_id = message_data.get("node_id")
            training_status = message_data.get("training_status")
            network_status = message_data.get("network_status")
            accuracy = message_data.get("accuracy")
            validation_accuracy = message_data.get("validation_accuracy")
            loss = message_data.get("loss")
            

            # Process based on the message type
            if msg_type == SEND_NETWORK_STATUS:
                self.handle_network_status(node_id,role, network_status)                
            elif msg_type == SEND_TRAINING_STATUS:
                self.handle_training_status(node_id,role, training_status)
            elif msg_type == RECEIVE_MODEL_INFO:
                self.handle_receive_model_info(node_id, accuracy,validation_accuracy,loss)
            elif msg_type == TERMINATE_API:
                self.handle_terminate_api(node_id,mqtt_obj)
            elif msg_type == PAUSE_API:
                self.handle_pause_api(node_id,mqtt_obj)
            elif msg_type == RESUME_API:
                self.handle_resume_api(node_id,mqtt_obj)



        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON message: {str(e)}")

    def handle_network_status(self, node_id,role, network_status):
        # Handle network status logic
        
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
            
        # self.logger.critical(f"Network status:{message_data}")
        # self.db.add_network_status(user_id, network_status)
        # self.logger.info(f"Received network status from user {user_id}: {network_status}")

    def handle_training_status(self, node_id,role, training_status):
        # Handle training status logic
        # Update database with training status
        # self.db.add_training_status(user_id, message_data)
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

    def handle_receive_model_info(self,node_id, accuracy,validation_accuracy,loss):
        # Handle received model information logic
        # Update database with received model information
        # self.db.add_received_model_info(user_id, message_data)
        data = {
            "training_info":1,
            "node_id": node_id,
            "accuracy": accuracy,
            "validation_accuracy":validation_accuracy,
            "loss":loss,
        }
        status = self.update_receive_model_info(data)
        if status:
            self.logger.critical(f"Received Model Information")
        else:
            self.logger.error("Not Received Model Information")

    def handle_terminate_api(self, user_id,mqtt_obj):
        # Handle terminate API logic
        # Update database with terminate status
        # self.db.update_terminate_status(user_id)
        message_json = json.dumps({
        "receiver": 'User',
        "role": 'Admin',

        "msg": TERMINATE_API,
        "Admin": id})
    
        
        self.logger.info(f"Terminated API for user {user_id}")

        # Send acknowledge termination to the user
        mqtt_obj.send_internal_messages(message_json)

    def handle_pause_api(self, user_id,mqtt_obj):
        # Handle pause API logic
        # Update database with pause status
        # self.db.update_pause_status(user_id)
        message_json = json.dumps({
        "receiver": 'User',
        "role": 'Admin',

        "msg": PAUSE_API,
        "Admin": id})

        self.logger.info(f"Paused API for user {user_id}")
        # Send acknowledge pause to the user

        mqtt_obj.send_internal_messages(message_json)



    def handle_resume_api(self, user_id):
        # Handle pause API logic
        # Update database with pause status
        # self.db.update_pause_status(user_id)
        message_json = json.dumps({
        "receiver": 'User',
        "role": 'Admin',
        "msg": RESUME_API,
        "Admin": id})
        self.logger.info(f"Resume API for user {user_id}")

        # Send acknowledge pause to the user
        self.mqtt_obj.send_internal_messages(message_json)


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
            response = self.apiClient.post_request(add_training_result, data)

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
    
    # def get_node_count(self):
    #     try:
    #         response = self.apiClient.get_request(node_id_count)

    #         if response.status_code == 200:
    #             count_data = response.json()
    #             user_count = count_data.get('count')
    #             return user_count
    #         else:
    #             print(f"GET Request Failed: {response.status_code}, {response.text}")
    #             return None
    #     except Exception as e:
    #         self.logger.error(f"Error in get_node_count: {str(e)}")
    #         return None
    
    # def add_global_model_hash(self, data):
    #     try:
    #         response = self.apiClient.post_request(add_global_model_hash, data)

    #         if response and response.status_code == 200:
    #             self.logger.info(f"POST add_global_model_hash Request Successful: {response.text}")
    #             return json.loads(response.text)
    #         else:
    #             self.logger.error(f"POST Request Failed: {response.status_code, response.text}")
    #             return None
    #     except Exception as e:
    #         self.logger.error(f"Error in add_global_model_hash: {str(e)}")
    #         return None
    
        
    # def perform_aggregation(self, user_model_hashes):
    #     try:
    #         aggregated_hash = hash(''.join(user_model_hashes))
    #         return aggregated_hash
    #     except Exception as e:
    #         self.logger.error(f"Error in perform_aggregation: {str(e)}")
    #         return None
    
    # def get_user_data(self):
    #     try:
    #         get_user = self.apiClient.get_request(get_admin_data)

    #         if get_user.status_code == 200:
    #             self.logger.info(f"Get Request Successful: {get_user.text}")
    #             return json.loads(get_user.text)
    #         else:
    #             self.logger.error(f"GET Request Failed: {get_user.status_code, get_user.text}")
    #             return None
    #     except Exception as e:
    #         self.logger.error(f"Error in get_user_data: {str(e)}")
    #         return None
    
    # def get_latest_global_model(self):
    #     try:
    #         get_model = self.apiClient.get_request(get_global_model_hash)

    #         if get_model.status_code == 200:
    #             self.logger.info(f"Get Request Successful: {get_model.text}")
    #             return json.loads(get_model.text)
    #         else:
    #             self.logger.error(f"GET Request Failed: {get_model.status_code, get_model.text}")
    #             return None
    #     except Exception as e:
    #         self.logger.error(f"Error in get_latest_global_model: {str(e)}")
    #         return None
    
    # def post_global_model(self, glb_hash=None):
    #     try:
    #         data = {
    #             "global_model_hash": glb_hash,
    #         }
    #         post_response = self.apiClient.post_request(endpoint=post_global_model_hash, data=data)
    #         if post_response.status_code == 201:
    #             self.logger.info(f"POST Request Successful: {post_response.text}")
    #             glb_data = json.loads(post_response.text)
    #             return glb_data['global_model_hash']
    #         else:
    #             self.logger.error(f"POST Request Failed: {post_response.status_code, post_response.text}")
    #             return None
    #     except Exception as e:
    #         self.logger.error(f"Error in post_global_model: {str(e)}")
    #         return None

    # def process_user_data(self, user_data):
    #     try:
    #         model_hash = user_data[0]['model_hash']
    #         self.model_list.append(model_hash)
    #         self.logger.info(f"Send global model: {self.model_list}")
    #     except Exception as e:
    #         self.logger.error(f"Error in process_user_data: {str(e)}")


    # def global_model_operations(self):
    #     try:
    #         self.global_model = self.ml_operations.aggregate_models(self.model_list)
    #         self.logger.info(f"Got Global model hash: {self.global_model}")

    #         global_hash = self.post_global_model(self.global_model)
    #         self.logger.info(self.ml_operations.send_global_model_to_others(self.mqtt_obj, global_hash))

    #         self.mqtt_obj.client_hash_mapping.clear()
    #         self.logger.info("Clear all hash operations")

    #         latest_global_model_hash = self.get_latest_global_model()
    #         self.logger.info(f"I am aggregator, here is the global model hash: {latest_global_model_hash['global_model_hash']}")
    #         self.ml_operations.is_global_model_hash(latest_global_model_hash)
    #     except Exception as e:
    #         self.logger.error(f"Error in global_model_operations: {str(e)}")