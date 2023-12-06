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

        
    

    def admin_logic(self):
        self.logger.info("I am Admin ")
        # self.mqtt_obj.send_head_id(self.id)
        # while self.is_running:
        #     self.logger.debug("Waiting")
        #TODO: if the user sending message using mqtt add user in database and also updates connected status
    
        admin_data = {
            "training_status": "in_progress",
            "role": "Admin",
            "node_id": 7,
            "model_hash": "your_model_hash_here",
            "network_status": "connected"
        }
   
        status=self.add_admin(admin_data)
        if status:
            self.logger.info("Added")
        else:
            self.logger.info("Not Added")
            
        #TODO: Check no_of_user in database
            # if the user is 1 do not aggregate and update the global model hash 
            # if user is more than 2 wait for their all their model hash then aggregation 

        user_count = self.get_node_count()

        # Check if the user count is 1 (no aggregation needed) or more than 2 (wait for all hashes)
        if user_count == 1:
            self.logger.debug("User count: 1")
            # If only one user, update the global model hash immediately
            #self.global_model_hash = user_model_hash
        elif user_count > 2:
            # If more than two users, wait for all users to submit their model hashes
            #self.user_model_hashes.add(user_model_hash)
            self.logger.debug("More than User count: 2")
            
            if len(self.user_model_hashes) == user_count:
                # Perform aggregation when all users have submitted their model hashes
                self.global_model_hash = self.perform_aggregation(self.user_model_hashes)
                self.aggregation_in_progress = False


           

    def add_admin(self, admin_data):
           
        # Assuming admin_data is a dictionary containing data for the Admin model
        admin_data_json = json.dumps(admin_data)

        response = self.apiClient.post_request(add_nodes, data=admin_data_json)

        if response and response.status_code == 201:
            self.logger.info(f"POST add_admin Request Successful: {response.text}")
            return json.loads(response.text)
        else:
            self.logger.info(f"POST Request Failed: {response.status_code, response.text}")
            return None
    
    def get_node_count(self):

        # Make the GET request using the get_request method
        response = self.apiClient.get_request(node_id_count)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response and get the user count
            count_data = response.json()
            user_count = count_data.get('count')
            return user_count
        else:
            # Handle the case where the request was not successful
            print(f"GET Request Failed: {response.status_code}, {response.text}")
            return None

    def perform_aggregation(self, user_model_hashes):
            # Placeholder for your aggregation logic
        # Replace this with your actual aggregation logic
        aggregated_hash = hash(''.join(user_model_hashes))
        return aggregated_hash
    
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
