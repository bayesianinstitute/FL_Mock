from core.MqttOPS.mqtt_operations import MqttOperations
import argparse

from core.Logs_System.logger import Logger

from core.API.ClientAPI import ApiClient
from core.API.endpoint import *
import json

import requests



# Define a class for the Federated Learning Workflow
class DFLWorkflow:
    def __init__(self, broker_service, internal_cluster_topic, cluster_name):
        
        self.ip='http://127.0.0.1' 
        # Setup Logger
        self.logger=Logger(name='DFL_logger',api_endpoint=f"{self.ip}:8000/{update_logs}").get_logger()
        # Initialize various attributes and parameters

        self.global_ipfs_link = None
        self.participant_identification = None
        self.broker_service = broker_service
        self.internal_cluster_topic = internal_cluster_topic
        self.mqtt_operations = None

        self.cluster_name=cluster_name


         
        self.apiClient=ApiClient(ip=self.ip)

    def get_public_ip(self):
        try:
            response = requests.get("https://api64.ipify.org?format=json")
            if response.status_code == 200:
                public_ip = response.json()["ip"]
                return f"http://{public_ip}"
            else:
                print(f"Failed to retrieve public IP. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error retrieving public IP: {e}")

    def update_role_status(self,data,role):

        try:
            if role =='User':

                connected_status = self.apiClient.put_request(update_user,data)

                if connected_status.status_code == 200:
                    self.logger.info(f"PUT  User Role_status Request Successful: {connected_status.text}")
                    return json.loads(connected_status.text)
                else:
                    self.logger.info(f"PUT  User Request Failed: {connected_status.status_code, connected_status.text}")
                    return None

            elif role =='Admin':

                connected_status = self.apiClient.put_request(update_admin,data)

                if connected_status.status_code == 200:
                    self.logger.info(f"PUT Admin Role_status Request Successful: {connected_status.text}")
                    return json.loads(connected_status.text)
                else:
                    self.logger.info(f"PUT Admin Request Failed: {connected_status.status_code, connected_status.text}")
                    return None
            else:
                import sys
                self.logger.critical(F"unknow role: {role} failed")
                sys.exit(1)

        except Exception as e:
                self.logger.error(f"Error in update_network_status: {str(e)}")
                return None
        else:
            pass
        
    # Main function to run the federated learning workflow
    def run(self,role='User'):

        self.logger.debug(self.internal_cluster_topic)

        self.logger.info(f"Your IP address is {self.ip}")

        data={
            "role":role
        }


        role_data=self.update_role_status(data,role)


        # Initialize  MQTT operations for communication
        self.mqtt_operations = MqttOperations(self.ip,self.internal_cluster_topic,
                                              self.cluster_name,
                                            self.broker_service,
                                            )

        if role_data['role'] == "Admin":
            from core.Role.Admin import Admin

            self.logger.info(f"Role Admin")

            model_type = 'CNN'

            optimizer = "Adam"  

            # Fetch from database
            data={
                    "model_name": model_type,
                    "dataset_name": "Mnist",
                    "optimizer": optimizer,
                    "training_name": self.internal_cluster_topic }    
            
            self.logger.warning(data)

            post_response=self.apiClient.post_request(create_training_information,data)

            if post_response.status_code == 201:
                self.logger.info(f"POST Request Successful: {post_response.text}" )
            else:
                self.logger.error(f"POST Request Failed:{ post_response.status_code, post_response.text}")

            admin = Admin(self.internal_cluster_topic , model_type, optimizer,self.mqtt_operations,self.ip,role=role_data['role'])
            admin.admin_logic()
        # User
        elif role_data['role'] == "User":
            from core.Role.User import User

            self.logger.info(f"Role User")
            user = User( self.internal_cluster_topic,self.mqtt_operations,self.ip,role=role_data['role'] )
            user.user_logic()
        else:
             pass

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("broker_service", help="Name of broker service", type=str)
    parser.add_argument("cluster_name", help="Name of the cluster", type=str)
    parser.add_argument("role", help="Name of role", type=str)


    args = parser.parse_args()


    internal_cluster_topic=f'{args.cluster_name}_topic'
    
    workflow = DFLWorkflow(args.broker_service,  internal_cluster_topic,args.cluster_name)
    workflow.run(args.role)