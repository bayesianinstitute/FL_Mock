from core.API.endpoint import *
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
            while(1):

                message_json = json.dumps({
                    "msg": "AFAAN",
                    "id": "user_status['id']",
                    "network_status": "user_status['network_status']"
                })
                mqtt_obj.send_internal_messages(message_json)
                
                admin_data = {
                    "training_status": "in_progress",
                    "role": "Admin",
                    "node_id": 8,
                    "model_hash": "your_model_hash_here",
                    "network_status": "connected"
                }

                status = self.add_admin(admin_data)
                if status:
                    self.logger.info("Added")
                else:
                    self.logger.error("Not Added")

                user_count = self.get_node_count()

                if user_count == 1:
                    self.logger.debug("User count: 1")
                    data = {
                        "global_model_hash": "HAsha256",
                    }

                    status = self.add_global_model_hash(data)
                    if status:
                        self.logger.debug("Added global model")
                    else:
                        self.logger.error("Not Added global model")
                elif user_count > 2:
                    self.logger.debug("More than User count: 2")
                    data = {
                        "global_model_hash": "HAsha256",
                    }

                    status = self.add_global_model_hash(data)
                    if status:
                        self.logger.debug("Added global model")
                    else:
                        self.logger.error("Not Added global model")

        except Exception as e:
            self.logger.error(f"Error in admin_logic: {str(e)}")
 
    def add_admin(self, admin_data):
        try:
            response = self.apiClient.post_request(add_nodes, admin_data)

            if response and response.status_code == 201:
                self.logger.info(f"POST add_admin Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                self.logger.error(f"POST Request Failed: {response.status_code, response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in add_admin: {str(e)}")
            return None
    
    def get_node_count(self):
        try:
            response = self.apiClient.get_request(node_id_count)

            if response.status_code == 200:
                count_data = response.json()
                user_count = count_data.get('count')
                return user_count
            else:
                print(f"GET Request Failed: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in get_node_count: {str(e)}")
            return None
    
    def add_global_model_hash(self, data):
        try:
            response = self.apiClient.post_request(add_global_model_hash, data)

            if response and response.status_code == 200:
                self.logger.info(f"POST add_global_model_hash Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                self.logger.error(f"POST Request Failed: {response.status_code, response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in add_global_model_hash: {str(e)}")
            return None
    
        
    def perform_aggregation(self, user_model_hashes):
        try:
            aggregated_hash = hash(''.join(user_model_hashes))
            return aggregated_hash
        except Exception as e:
            self.logger.error(f"Error in perform_aggregation: {str(e)}")
            return None
    
    def get_user_data(self):
        try:
            get_user = self.apiClient.get_request(get_admin_data)

            if get_user.status_code == 200:
                self.logger.info(f"Get Request Successful: {get_user.text}")
                return json.loads(get_user.text)
            else:
                self.logger.error(f"GET Request Failed: {get_user.status_code, get_user.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in get_user_data: {str(e)}")
            return None
    
    def get_latest_global_model(self):
        try:
            get_model = self.apiClient.get_request(get_global_model_hash)

            if get_model.status_code == 200:
                self.logger.info(f"Get Request Successful: {get_model.text}")
                return json.loads(get_model.text)
            else:
                self.logger.error(f"GET Request Failed: {get_model.status_code, get_model.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in get_latest_global_model: {str(e)}")
            return None
    
    def post_global_model(self, glb_hash=None):
        try:
            data = {
                "global_model_hash": glb_hash,
            }
            post_response = self.apiClient.post_request(endpoint=post_global_model_hash, data=data)
            if post_response.status_code == 201:
                self.logger.info(f"POST Request Successful: {post_response.text}")
                glb_data = json.loads(post_response.text)
                return glb_data['global_model_hash']
            else:
                self.logger.error(f"POST Request Failed: {post_response.status_code, post_response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in post_global_model: {str(e)}")
            return None

    def process_user_data(self, user_data):
        try:
            model_hash = user_data[0]['model_hash']
            self.model_list.append(model_hash)
            self.logger.info(f"Send global model: {self.model_list}")
        except Exception as e:
            self.logger.error(f"Error in process_user_data: {str(e)}")


    def global_model_operations(self):
        try:
            self.global_model = self.ml_operations.aggregate_models(self.model_list)
            self.logger.info(f"Got Global model hash: {self.global_model}")

            global_hash = self.post_global_model(self.global_model)
            self.logger.info(self.ml_operations.send_global_model_to_others(self.mqtt_obj, global_hash))

            self.mqtt_obj.client_hash_mapping.clear()
            self.logger.info("Clear all hash operations")

            latest_global_model_hash = self.get_latest_global_model()
            self.logger.info(f"I am aggregator, here is the global model hash: {latest_global_model_hash['global_model_hash']}")
            self.ml_operations.is_global_model_hash(latest_global_model_hash)
        except Exception as e:
            self.logger.error(f"Error in global_model_operations: {str(e)}")