import sys
from core.MqttOPS.mqtt_operations import MqttOperations
from core.MLOPS.ml_operations import MLOperations
import argparse

# from core.FL_System.identifyparticipants.identify_participants import IdentifyParticipant
import uuid
from core.Logs_System.logger import Logger

from core.API.ClientAPI import ApiClient
from core.API.endpoint import *
import json



# Define a class for the Federated Learning Workflow
class DFLWorkflow:
    def __init__(self, broker_service, internal_cluster_topic, cluster_name, id,
                 voting_topic, declare_winner_topic, min_node, updated_broker, training_type, optimizer):
        
        # Setup Logger
        self.logger=Logger(name='DFL_logger').get_logger()
        # Initialize various attributes and parameters

        self.global_ipfs_link = None
        self.participant_identification = None
        self.broker_service = broker_service
        self.internal_cluster_topic = internal_cluster_topic
        self.mqtt_operations = None
        self.optimizer = optimizer
        self.training_type=training_type
        self.global_model = None

        self.cluster_name=cluster_name

        self.voting_topic = voting_topic
        self.winner_declare = declare_winner_topic

        self.id = f'{id}-{uuid.uuid4()}'  # Create a unique client ID with a UUID
        self.is_admin = None
        self.min_node = min_node
        self.updated_broker = updated_broker

        self.apiClient=ApiClient()

    # Function to terminate the program
    def terminate_program(self):
        self.logger.warning("Terminated program successfully ")
        sys.exit()

    # Main function to run the federated learning workflow
    def run(self):

        data={
        "Model name:": self.training_type,
        "Dataset name": "Mnist",
        "Optimizer": self.optimizer,
        "Training name": self.cluster_name }    
        
        print(data)

        # post_response=self.apiClient.post_request(create_training_information_endpoint,data)

        # if post_response.status_code == 201:
        #     self.logger.info(f"POST Request Successful: {post_response.text}" )
        # else:
        #     self.logger.error(f"POST Request Failed:{ post_response.status_code, post_response.text}")

        self.logger.debug(self.internal_cluster_topic)
        self.logger.debug(self.id)

        get_role=self.apiClient.get_request(get_track_role)

        if get_role.status_code == 200:
            self.logger.info(f"Get Request Successful: {get_role.text}" )
            role_data = json.loads(get_role.text)
            print(role_data['role'])
        else:
            self.logger.error(f"GET Request Failed:{ get_role.status_code, get_role.text}")

        Round_Counter = 0

        # Initialize  MQTT operations for communication
        self.mqtt_operations = MqttOperations(self.internal_cluster_topic,
                                              self.cluster_name,
                                            self.broker_service,
                                            self.min_node,
                                            self.is_admin,
                                            self.id)

        # while True:n
            # TODO:  Need api to update training rounds 
        Round_Counter = Round_Counter + 1
        self.logger.info(f"Round_Counter: {Round_Counter}")
        # Admin
        if role_data['role'] == "Admin":
            from core.Role.Admin import Admin

            self.logger.info(f"Admin")

            admin = Admin(self.internal_cluster_topic , self.training_type, self.optimizer,self.mqtt_operations,role=role_data['role'],)
            admin.admin_logic(self.id)
        # User
        elif role_data['role'] == "User":
            from core.Role.User import User

            self.logger.info(f"User")
            user = User( self.internal_cluster_topic,self.mqtt_operations,role=role_data['role'] )
            # call  shell mlflow on this FL_Mock\core\MLOPS\Model> mlflow ui
            user.user_logic()
        else:
             pass
                # Temporary to close the program
            # if Round_Counter == 2:
                    
            #         break
            # self.logger.info(f"Training completed with round {Round_Counter} !! ")


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
    print("Hello")
    voting_topic = f'Voting/{args.cluster_name}'
    declare_winner_topic = f'Winner/{args.cluster_name}'

    internal_cluster_topic='internal_cluster_topic'
    
    workflow = DFLWorkflow(args.broker_service,  internal_cluster_topic,args.cluster_name, args.id,
                           voting_topic, declare_winner_topic, args.min_node, updated_broker, model_type, optimizer)
    workflow.run()