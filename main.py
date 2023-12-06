import sys
import argparse

# from core.FL_System.identifyparticipants.identify_participants import IdentifyParticipant
import uuid
from core.Logs_System.logger import Logger

from core.API.ClientAPI import ApiClient
from core.API.endpoint import *
import json
from core.MqttOPS.mqtt_operations import MqttOperations

from core.MLOPS.ml_operations import MLOperations

from core.Role.Admin import AdminOPS
from core.Role.User import UserOPS

class DFLWorkflow:
    def __init__(self, broker_service, internal_cluster_topic, cluster_name, id, voting_topic, declare_winner_topic,
                 min_node, updated_broker, training_type, optimizer):
        self.logger = Logger(name='DFL_logger').get_logger()
        self.broker_service = broker_service
        self.internal_cluster_topic = internal_cluster_topic
        self.optimizer = optimizer
        self.training_type = training_type
        self.cluster_name = cluster_name
        self.voting_topic = voting_topic
        self.winner_declare = declare_winner_topic
        self.id = f'{id}-{uuid.uuid4()}'
        self.is_admin = None
        self.min_node = min_node
        self.updated_broker = updated_broker
        self.apiClient = ApiClient()

        
        self.ml_operations = MLOperations(training_type, optimizer)
        self.mqtt_operations = MqttOperations(internal_cluster_topic, cluster_name,
                                              broker_service, min_node, self.is_admin, id)
        
        self.mqtt_obj = self.mqtt_operations.start_dfl_using_mqtt()

        self.admin = AdminOPS(self.mqtt_obj,self.ml_operations)
        self.user = UserOPS(self.mqtt_obj,self.ml_operations)

    def terminate_program(self):
        self.logger.warning("Terminated program successfully ")
        sys.exit()

    def run(self):
        data = {
            "model_name": self.training_type,
            "dataset_name": "Mnist",
            "optimizer": self.optimizer,
            "training_name": self.cluster_name
        }

        self.logger.info("Initializing federated learning workflow...")

        post_response = self.apiClient.post_request(create_training_information_endpoint, data)

        if post_response.status_code == 201:
            self.logger.info(f"POST Request Successful: {post_response.text}")
        else:
            self.logger.error(f"POST Request Failed: {post_response.status_code, post_response.text}")

        role_data = self.get_role_data()

        if role_data['role'] == "Admin":
            self.admin_logic()
        elif role_data['role'] == "User":
            self.user_logic()
        else:
            pass  # Temporary to close the program


    def get_role_data(self):
        get_role = self.apiClient.get_request(get_track_role)

        if get_role.status_code == 200:
            self.logger.info(f"Get Request Successful: {get_role.text}")
            return json.loads(get_role.text)
        else:
            self.logger.error(f"GET Request Failed: {get_role.status_code, get_role.text}")
            return {}

    def admin_logic(self):
        self.logger.info(f"Admin")
        self.admin.admin_logic()

    def user_logic(self):
        self.logger.info(f"User")
        self.user.user_logic()
        
if __name__ == "__main__":
    try:
        # Try to open the configuration file
        with open("config/config.json", "r") as file:
            config = json.load(file)
    except FileNotFoundError:
        print("Error: config.json not found. Please create the file with the necessary configuration.")
        sys.exit(1)

    print(f"Config {config}")
    # Extract values from the configuration file
    broker_service = config['DFL_Config'].get("broker_service")
    cluster_name = config['DFL_Config'].get("cluster_name")
    client_id = config['DFL_Config'].get("id")
    min_node = config['DFL_Config'].get("min_node")
    updated_broker = config['DFL_Config'].get("updated_broker")
    model_type = config['DFL_Config'].get("model_type")
    optimizer = config['DFL_Config'].get("optimizer")

    voting_topic = f'Voting/{cluster_name}'
    declare_winner_topic = f'Winner/{cluster_name}'
    internal_cluster_topic = f'{cluster_name}/internal_cluster_topic'


    # Create DFLWorkflow instance with configuration values
    workflow = DFLWorkflow(broker_service, internal_cluster_topic, cluster_name, client_id,
                           voting_topic, declare_winner_topic, min_node,
                           updated_broker,
                           model_type,
                           optimizer)
    workflow.run()
