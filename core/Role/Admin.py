from core.API.endpoint import *
import json

from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
# admin_module.py

class Admin:
    def __init__(self, training_type, optimizer):
        self.apiClient=ApiClient()
        self.ml_operations = MLOperations(training_type, optimizer)

        self.logger = Logger(name='admin-role').get_logger()

        self.model_list = []

    def admin_logic(self,  mqtt_obj,id):
        self.is_admin = True
        self.logger.info("I am Admin ")
        mqtt_obj.send_head_id(id)
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
        model_hash = user_data['model_hash']
        self.model_list.append(model_hash)
        self.logger.info(f"Send global model:{ self.model_list}")
        
        # Send all the list of hashes to aggregate and get the global model hash
        self.global_model = self.ml_operations.aggregate_models(self.model_list)
        
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
