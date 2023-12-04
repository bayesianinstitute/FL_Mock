from core.API.endpoint import *
import json

# admin_module.py
from core.Logs_System.logger import Logger

class Admin:
    def __init__(self, apiClient, ml_operations, mqtt_operations,logger):
        self.apiClient = apiClient
        self.ml_operations = ml_operations
        self.mqtt_operations = mqtt_operations
        self.logger = logger

    def admin_logic(self, role_data, mqtt_obj):
        self.is_admin = True
        self.logger.info("I am Admin ")
        mqtt_obj.send_head_id(self.id)
        # TODO: get status of client using mqtt
        # instead of managing a list of hashes need an API to get all work hash
        get_user = self.apiClient.get_request(get_admin_data)
        if get_user.status_code == 200:
            self.logger.info(f"Get Request Successful: {get_user.text}")
            user_data = json.loads(get_user.text)
            print(user_data)
        else:
            self.logger.error(f"GET Request Failed:{ get_user.status_code, get_user.text}")
        
        # TODO:  Get API all client model hash and need logic to check if we get all hashes from all workers
        get_list = user_data['model_hash']
        self.logger.info(f"Send global model:{ get_list}")
        
        # Send all the list of hashes to aggregate and get the global model hash
        self.global_model = self.ml_operations.aggregate_models(get_list)
        
        # TODO:  post API to add the latest global model hash
        self.logger.info(f"Got Global model hash: {self.global_model}")
        
        # Sending global model hash to all workers
        self.logger.info(self.ml_operations.send_global_model_to_others(mqtt_obj, self.global_model))
        
        # Clearing all previous model hashes from all workers
        mqtt_obj.client_hash_mapping.clear()
        self.logger.info("Clear all hash operations")
        
        # TODO: Get API the latest global model hash
        latest_global_model_hash = mqtt_obj.global_model()
        self.logger.info(f"I am aggregator, here is the global model hash:{ latest_global_model_hash}")
        
        # Set the latest global model hash and set weights in MLOperation
        self.ml_operations.is_global_model_hash(latest_global_model_hash)
