import sys
from core.MqttOPS.mqtt_operations import MqttOperations
from core.MLOPS.ml_operations import MLOperations
import argparse

from core.FL_System.identifyparticipants.identify_participants import IdentifyParticipant
import uuid
from core.Logs_System.logger import Logger

from core.API.ClientAPI import ApiClient
from core.API.endpoint import *
import json

# Define a class for the Federated Learning Workflow
class DFLWorkflow:
    def __init__(self,
                 broker_service,
                 internal_cluster_topic,
                 cluster_name,
                 id,
                 voting_topic,
                 declare_winner_topic,
                 min_node,
                 updated_broker,
                 training_type,
                 optimizer,
                 ):
        
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
        self.ml_operations = MLOperations(self.training_type, self.optimizer)
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
        "model_name": self.training_type,
        "dataset_name": "Mnist",
        "optimizer": self.optimizer,
        "training_name": self.cluster_name }    
        
        print(data)

        post_response=self.apiClient.post_request(create_training_information_endpoint,data)

        if post_response.status_code == 201:
            self.logger.info(f"POST Request Successful: {post_response.text}" )
        else:
            self.logger.error(f"POST Request Failed:{ post_response.status_code, post_response.text}")

        self.logger.debug(self.internal_cluster_topic)
        self.logger.debug(self.id)

        get_role=self.apiClient.get_request(get_track_role)

        if get_role.status_code == 200:
            self.logger.info(f"Get Request Successful: {get_role.text}" )
            role_data = json.loads(get_role.text)
            print(role_data['role'])


        else:
            self.logger.error(f"GET Request Failed:{ get_role.status_code, get_role.text}")

        try:
            get_list = None
            Round_Counter = 0

            # Create an instance of IdentifyParticipant and  to do voting if the client is a worker or head
            # self.participant = IdentifyParticipant(
            #     self.id, self.broker_service, self.voting_topic, self.winner_declare, self.min_node)
        
            # self.is_admin = self.participant.main()

            # Initialize  MQTT operations for communication
            self.mqtt_operations = MqttOperations(self.internal_cluster_topic,
                                                  self.cluster_name,
                                                self.broker_service,
                                                self.min_node,
                                                self.is_admin,
                                                self.id)

            # Start, initialize, and get MQTT communication object
            mqtt_obj = self.mqtt_operations.start_dfl_using_mqtt()

            while True:

                # TODO:  Need api to update training rounds 

                Round_Counter = Round_Counter + 1
                self.logger.info(f"Round_Counter: {Round_Counter}")

                if role_data['role']=="Admin":
                    self.is_admin=True
                    self.logger.info(f"I am Admin " )
                    mqtt_obj.send_head_id(self.id)                    
                    # TODO : get status of client using mqtt
                    # instead managing list of hashes need api to get all work hash
                    get_user=self.apiClient.get_request(get_admin_data)
                    if get_user.status_code == 200:
                        self.logger.info(f"Get Request Successful: {get_user.text}" )
                        user_data = json.loads(get_user.text)
                        print(user_data)
                    else:
                        self.logger.error(f"GET Request Failed:{ get_role.status_code, get_role.text}")
                    # TODO:  Get api all client model hash and need logic to check if we get all hashes from all workers
                    get_list = user_data['model_hash']
                    self.logger.info(f"Send global model:{ get_list}")
                    # Send all the list of hashes to aggregate and get the global model hash
                    self.global_model = self.ml_operations.aggregate_models(get_list)
                    # TODO:  post api to add latest global model hash
                    self.logger.info(f"Got Global model hash: {self.global_model}" )
                    # Sending global model hash to all workers
                    self.logger.info(self.ml_operations.send_global_model_to_others(mqtt_obj, self.global_model))
                    # Clearing all previous model hashes from all workers
                    mqtt_obj.client_hash_mapping.clear()
                    self.logger.info("Clear all hash operations")
                    # TODO: Get api the latest global model hash
                    latest_global_model_hash = mqtt_obj.global_model()
                    self.logger.info(f"I am aggregator, here is the global model hash:{ latest_global_model_hash}")
                    # Set the latest global model hash and set weights in MLOperation
                    self.ml_operations.is_global_model_hash(latest_global_model_hash)

                elif role_data['role']=="User":
                    self.is_admin=False

                    self.logger.info(f"I am User!" )

                    # Update connected Status
                    connected_status=self.apiClient.put_request(network_connected_endpoint)
                    if connected_status.status_code == 200:
                            print("PUT network_status Request Successful:", connected_status.text)
                            user_status = json.loads(connected_status.text)
                            message = "connection_status"
                            message_json = json.dumps({
                                "msg": message,
                                "id": user_status['id'],
                                "network_status": user_status['network_status']
                            })
                            mqtt_obj.send_internal_messages(message_json)
                    else:
                            print("PUT Request Failed:", connected_status.status_code, connected_status.text)

                    # Update training Status
                    training_status=self.apiClient.put_request(toggle_training_status_endpoint)
                    if training_status.status_code == 200:
                        print("PUT training_status Request Successful:",training_status.text)
                        user_status = json.loads(training_status.text)
                        message= "training_status"
                        message_json = json.dumps({
                                "msg": message,
                                "id": user_status['id'],
                                "training_status": user_status['training_status'],
                            })
                        mqtt_obj.send_internal_messages(message_json)
                    else:
                        print("PUT Request Failed:", training_status.status_code, training_status.text)


                    hash,accuracy,loss = self.ml_operations.train_machine_learning_model()
                    self.logger.info(f"Model hash: {hash}" )


                    # TODO: Need post api to update latest training model hash
                    # Send the model to the internal cluster
                    message_json =json.dumps({
                        "client_id": user_status['id'],
                        "model_hash": hash,
                        "accuracy":accuracy,
                        "loss":loss,
                    })

                    mqtt_obj.send_internal_messages_model(message_json)

                    # Get the latest global model hash
                    self.terminate_program()

                    latest_global_model_hash = mqtt_obj.global_model()
                    # TODO:  post api to add latest global model hash
                    self.logger.info(f"I am not aggregator, got global model hash: { latest_global_model_hash}")
                    # Set the latest global model hash and set weights in MLOperation
                    self.ml_operations.is_global_model_hash(latest_global_model_hash)
                    mqtt_obj.global_model_hash=None

                    # Temporary to close the program
                if Round_Counter == 6:
                        break

                self.logger.info(f"Training completed with round {Round_Counter} !! ")
            
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

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
