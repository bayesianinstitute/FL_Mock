import sys
import argparse

# from core.FL_System.identifyparticipants.identify_participants import IdentifyParticipant
import uuid
from core.Logs_System.logger import Logger

from core.API.ClientAPI import ApiClient
from core.API.endpoint import *
import json

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
        self.admin = AdminOPS(self.training_type, self.optimizer,self.internal_cluster_topic, self.cluster_name,
                                              self.broker_service, self.min_node, self.is_admin, self.id)
        self.user = UserOPS(self.training_type, self.optimizer,self.internal_cluster_topic, self.cluster_name,
                                              self.broker_service, self.min_node, self.is_admin, self.id)

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
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("broker_service", help="Name of broker service", type=str)
    parser.add_argument("cluster_name", help="Name of the cluster", type=str)
    parser.add_argument("id", help="client_id", type=str)
    parser.add_argument("min_node", help="minimum Node", type=int)

    updated_broker = 'broker.hivemq.com'

    model_type = 'CNN'

    optimizer = "Adam"

    args = parser.parse_args()

    voting_topic = f'Voting/{args.cluster_name}'
    declare_winner_topic = f'Winner/{args.cluster_name}'

    internal_cluster_topic=f'{args.cluster_name}/internal_cluster_topic'
    
    workflow = DFLWorkflow(args.broker_service,  internal_cluster_topic,args.cluster_name, args.id,
                           voting_topic, declare_winner_topic, args.min_node, updated_broker, model_type, optimizer)
    workflow.run()
