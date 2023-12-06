from core.API.endpoint import *
import json

from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
from core.MqttOPS.mqtt_operations import MqttOperations
import time

class AdminOPS:
    def __init__(self,mqtt_comm_obj,ml_ops_obj):
        self.logger = Logger(name='user-role').get_logger()
        self.apiClient = ApiClient()
        self.ml_operations = ml_ops_obj        
        self.mqtt_obj = mqtt_comm_obj
        self.model_list=[]

        
    

    def admin_logic(self, ):
        
        self.logger.info("I am Admin ")
    


        while True:

            self.logger.debug(f'Waiting for')

            time.sleep(5)
    
         
            user_data = self.get_user_data()
            
            if user_data:
                self.process_user_data(user_data)
            else:
                self.logger.error("Failed to retrieve user data")


            self.global_model_operations()



    def get_user_data(self):
        
        get_user = self.apiClient.get_request(get_admin_data)

        if get_user.status_code == 200:
            self.logger.info(f"Get Request Successful: {get_user.text}")
            return json.loads(get_user.text)
        else:
            self.logger.error(f"GET Request Failed: {get_user.status_code, get_user.text}")
            return None
    
    def get_latest_global_model(self):
        
        get_model = self.apiClient.get_request(get_global_model_hash)

        if get_model.status_code == 200:
            self.logger.info(f"Get Request Successful: {get_model.text}")
            return json.loads(get_model.text)
        else:
            self.logger.error(f"GET Request Failed: {get_model.status_code, get_model.text}")
            return None
    
    def post_global_model(self,glb_hash=None):
        data = {
        "global_model_hash": glb_hash,}
        post_response = self.apiClient.post_request(endpoint=post_global_model_hash, data=data)
        if post_response.status_code == 201:
            self.logger.info(f"POST Request Successful: {post_response.text}" )
            glb_data=json.loads(post_response.text)
            return glb_data['global_model_hash']

        else:
            self.logger.error(f"POST Request Failed: {post_response.status_code, post_response.text}")

    def process_user_data(self, user_data):

        model_hash = user_data[0]['model_hash']
        self.model_list.append(model_hash)
        self.logger.info(f"Send global model: {self.model_list}")

    def global_model_operations(self, ):
        # Send all the list of hashes to aggregate and get the global model hash
        self.global_model = self.ml_operations.aggregate_models(self.model_list)

        self.logger.info(f"Got Global model hash: {self.global_model}")
        
        global_hash=self.post_global_model(self.global_model)

        # Sending global model hash to all workers
        
        self.logger.info(self.ml_operations.send_global_model_to_others(self.mqtt_obj, global_hash))

        # Clearing all previous model hashes from all workers
        self.mqtt_obj.client_hash_mapping.clear()
        self.logger.info("Clear all hash operations")

        latest_global_model_hash = self.get_latest_global_model()

        self.logger.info(f"I am aggregator, here is the global model hash: {latest_global_model_hash['global_model_hash']}")
        self.ml_operations.is_global_model_hash(latest_global_model_hash)
