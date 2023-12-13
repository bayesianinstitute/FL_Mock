from core.MqttOPS.mqtt_operations import MqttOperations
import argparse

from core.Logs_System.logger import Logger

from core.API.ClientAPI import ApiClient
from core.API.endpoint import *
import json



# Define a class for the Federated Learning Workflow
class DFLWorkflow:
    def __init__(self, broker_service, internal_cluster_topic, cluster_name, 
                  training_type, optimizer):
        
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


        self.is_admin = None
         
        self.apiClient=ApiClient()

    # Main function to run the federated learning workflow
    def run(self):

        self.logger.debug(self.internal_cluster_topic)

        get_role=self.apiClient.get_request(get_track_role)

        if get_role.status_code == 200:
            self.logger.info(f"Get Request Successful: {get_role.text}" )
            role_data = json.loads(get_role.text)
            print(role_data['role'])
        else:
            self.logger.error(f"GET Request Failed:{ get_role.status_code, get_role.text}")

        # Initialize  MQTT operations for communication
        self.mqtt_operations = MqttOperations(self.internal_cluster_topic,
                                              self.cluster_name,
                                            self.broker_service,
                                            )

        if role_data['role'] == "Admin":
            from core.Role.Admin import Admin

            self.logger.info(f"Role Admin")


            data={
                    "model_name": self.training_type,
                    "dataset_name": "Mnist",
                    "optimizer": self.optimizer,
                    "training_name": self.internal_cluster_topic }    
            
            self.logger.warning(data)

            post_response=self.apiClient.post_request(create_training_information,data)

            if post_response.status_code == 201:
                self.logger.info(f"POST Request Successful: {post_response.text}" )
            else:
                self.logger.error(f"POST Request Failed:{ post_response.status_code, post_response.text}")

            admin = Admin(self.internal_cluster_topic , self.training_type, self.optimizer,self.mqtt_operations,role=role_data['role'],)
            admin.admin_logic()
        # User
        elif role_data['role'] == "User":
            from core.Role.User import User

            self.logger.info(f"Role User")
            user = User( self.internal_cluster_topic,self.mqtt_operations,role=role_data['role'] )
            user.user_logic()
        else:
             pass

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("broker_service", help="Name of broker service", type=str)
    parser.add_argument("cluster_name", help="Name of the cluster", type=str)


    model_type = 'CNN'

    optimizer = "Adam"

    args = parser.parse_args()


    internal_cluster_topic=f'{args.cluster_name}_topic'
    
    workflow = DFLWorkflow(args.broker_service,  internal_cluster_topic,args.cluster_name, model_type, optimizer)
    workflow.run()