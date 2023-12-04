from core.API.endpoint import *
import json

from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
from core.MqttOPS.mqtt_operations import MqttOperations

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



    def admin_logic(self, ):
        
        self.is_admin = True
        self.logger.info("I am Admin ")
        self.mqtt_obj.send_head_id(self.id)

        user_data = self.get_user_data()

        if user_data:
            self.process_user_data(user_data)
        else:
            self.logger.error("Failed to retrieve user data")

        self.global_model_operations()

    def get_user_data(self):
        # TODO: get status of client using mqtt
        get_user = self.apiClient.get_request(get_admin_data)

        if get_user.status_code == 200:
            self.logger.info(f"Get Request Successful: {get_user.text}")
            return json.loads(get_user.text)
        else:
            self.logger.error(f"GET Request Failed: {get_user.status_code, get_user.text}")
            return None

    def process_user_data(self, user_data):
        # TODO:  Get API all client model hash and need logic to check if we get all hashes from all workers
        model_hash = user_data.get('model_hash')
        self.model_list.append(model_hash)
        self.logger.info(f"Send global model: {self.model_list}")

    def global_model_operations(self, ):
        # Send all the list of hashes to aggregate and get the global model hash
        self.global_model = self.ml_operations.aggregate_models(self.model_list)

        # TODO:  post API to add the latest global model hash
        self.logger.info(f"Got Global model hash: {self.global_model}")

        # Sending global model hash to all workers
        
        self.logger.info(self.ml_operations.send_global_model_to_others(self.mqtt_obj, self.global_model))

        # Clearing all previous model hashes from all workers
        self.mqtt_obj.client_hash_mapping.clear()
        self.logger.info("Clear all hash operations")

        # TODO: Get API the latest global model hash
        latest_global_model_hash = self.mqtt_obj.global_model()
        self.logger.info(f"I am aggregator, here is the global model hash: {latest_global_model_hash}")

        # Set the latest global model hash and set weights in MLOperation
        self.ml_operations.is_global_model_hash(latest_global_model_hash)
