from core.API.endpoint import *
import json

from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
from core.MqttOPS.mqtt_operations import MqttOperations
import time

class AdminOPS:
    def __init__(self, training_type, optimizer,
                 internal_cluster_topic, cluster_name,
                broker_service, min_node, is_admin, id):
        self.apiClient = ApiClient()
        self.ml_operations = MLOperations(training_type, optimizer)
        self.mqtt_operations = MqttOperations(internal_cluster_topic, cluster_name,
                                              broker_service, min_node, is_admin, id)
        
        self.model_list = []
        self.id=id
        self.mqtt_obj = self.mqtt_operations.start_dfl_using_mqtt()
        self.logger = Logger(name='admin-role').get_logger()

        self.is_running = True  # Flag to control whether the program should run or stop

    def stop_program(self):
        self.is_running = False
        self.logger.warning(f"Stopping message")
        self.mqtt_obj.send_terminate_message("terimate msg from admin")
        self.logger.info(f"Status {self.mqtt_obj.terimate_status}")

        # Wait for acknowledgment
        while self.mqtt_obj.terimate_status==False:
            self.logger.debug(f"Waiting for status {self.mqtt_obj.terimate_status} ")
            time.sleep(8)

        self.logger.warning("Received acknowledgment. Stopping the program.")


    # def admin_logic(self, ):
        
    #     self.logger.info("I am Admin ")
    #     self.mqtt_obj.send_head_id(self.id)
    #     while self.is_running:
    
         
    #         user_data = self.get_user_data()
            
    #         if user_data:
    #             self.process_user_data(user_data)
    #         else:
    #             self.logger.error("Failed to retrieve user data")

    #         self.global_model_operations()
       
    def admin_logic(self):
        self.logger.info("I am Admin ")
        self.mqtt_obj.send_head_id(self.id)

        # TODO: Check no_of_user in the database
        no_of_users = self.get_number_of_users()

        while self.is_running:
            user_data = self.get_user_data()

            if user_data:
                self.process_user_data(user_data)
            else:
                self.logger.error("Failed to retrieve user data")

            # If there is only one user, do not aggregate and update the global model hash
            if no_of_users == 1:
                self.logger.info("Only one user. Skipping aggregation.")
                self.send_updated_global_model()

            # If there are more than two users, wait for their model hashes and perform aggregation
            elif no_of_users > 2 and len(self.model_list) == no_of_users:
                self.logger.info(f"All {no_of_users} users have sent their model hashes. Performing aggregation.")
                self.global_model_operations()
                self.send_updated_global_model()
            else:
                self.logger.info(f"Waiting for model hashes from users. {len(self.model_list)}/{no_of_users} received.")



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
