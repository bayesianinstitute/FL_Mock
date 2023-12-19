import json
import time

from core.API.endpoint import *
from core.Role.MsgType import *

from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
class User:
    def __init__(self,training_name,mqtt_operations,ip,role='User'):
        self.ip=ip
        self.apiClient=ApiClient(ip=self.ip)
        self.training_name=training_name
        self.ml_operations = None
        self.logger = Logger(name='user-role',api_endpoint=f"{self.ip}:8000/{update_logs}").get_logger()
        self.pause_training = False
        # Start, initialize, and get MQTT communication object
        self.mqtt_obj = mqtt_operations.start_dfl_using_mqtt(role)
        self.grant_received = False
        self.id= self.mqtt_obj.id

     



    def user_logic(self):
        rounds = 0
        self.join_training_network()


        self.logger.debug(f"Waiting for grant request from admin")
        try:

            while not self.grant_received:
                initial_received_message = self.mqtt_obj.handle_user_data()
                if initial_received_message:
                    self.process_initial_message(initial_received_message)

            user_status = self.update_network_status()
            self.send_network_status(user_status)



            while True:

                received_message = self.mqtt_obj.handle_user_data()
                if received_message:
                    self.process_received_message(received_message)


                if not self.pause_training:
                    rounds = rounds + 1


                    hash, final_accuracy, final_loss, val_acc, _ = self.ml_operations.train_machine_learning_model(
                        rounds=rounds, epochs=5, batch_size=32
                    )
                    self.logger.info(f"Model hash: {hash}")
                    data={
                        "accuracy": final_accuracy,
                        "training_accuracy": val_acc,
                        "loss": final_loss,
                        "training_info_name": self.training_name,
                        "model_hash": hash
                        }

                    self.store_user_data(data,create_training_result)

                    db_model={
                        "model_hash": hash
                    }

                    self.update_model_status(db_model)

                    self.send_model_to_internal_cluster(
                        user_status, hash,self.training_name, final_accuracy, final_loss
                    )

        except Exception as e:
            self.logger.error(f"Error in user_logic: {str(e)}")

        
    def update_global_model(self, data):
        try:
            response = self.apiClient.post_request(post_global_model_hash, data)

            if response and response.status_code == 201:
                self.logger.info(f"POST Global model Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                self.logger.error(f"POST Global model Request Failed: {response.status_code, response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in update global model: {str(e)}")
            return None

    def store_user_data(self, data,endpoint=None):
        try:
            response = self.apiClient.post_request(endpoint, data)

            if response and response.status_code == 201:
                self.logger.info(f"POST create user Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                self.logger.error(f"POST Request Failed: {response.status_code, response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in add_admin: {str(e)}")
            return None

    def handle_config(self,data):
        # Use the get function to retrieve values

        training_name = data.get("training_name")
        model_name = data.get("model_name")
        dataset_name = data.get("dataset_name")
        optimizer = data.get("optimizer")

        db_data={
            "model_name": model_name,
            "dataset_name": dataset_name,
            "optimizer": optimizer,
            "training_name": training_name
        }

        self.logger.info(f"model_type {model_name} , optimizer {optimizer} dataset : {dataset_name}")
        # add configuration in database
        self.store_user_data(db_data,create_training_information)

        self.ml_operations = MLOperations(self.ip,model_name, optimizer,training_name=f'{self.training_name}_client')


    def process_initial_message(self, data):
        try:
            if isinstance(data, str):
                message_data = json.loads(data)
            elif isinstance(data, bytes):
                message_data = json.loads(data.decode('utf-8'))
            else:
                message_data = data.get()

            msg_type = message_data.get("msg")

            if msg_type == GRANTED_JOIN:
                self.handle_config(message_data)
                self.grant_received = True


                


        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error in process_received_message: {str(e)}")

    def join_training_network(self, ):
        try:
                message_json = json.dumps({
                    "receiver": 'Admin',
                    "role": 'User',
                    "msg": JOIN_OPERATION,
                    "training_name": self.training_name,
                    "node_id": self.id
                })
                self.mqtt_obj.send_internal_messages(message_json)
                self.logger.info(f"sucessfully sent Joined training network")

        except Exception as e:
            self.logger.error(f"Error in send_network_status: {str(e)}")
   
    def update_operation_status(self, data):

        try:
            self.logger.info(f'Updating operation status {data}')
            response = self.apiClient.put_request(update_model_hash, data)

            if response and response.status_code == 200:
                self.logger.info(f"update_operation_status Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                # self.logger.error(f"update_operation_status  Request Failed: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error in add_admin: {str(e)}")
            return None

    def update_model_status(self, data):

        try:
            response = self.apiClient.put_request(update_model_hash, data)

            if response and response.status_code == 200:
                self.logger.info(f"update_model_status Request Successful: {response.text}")
                return json.loads(response.text)
            else:
                self.logger.error(f"update_model_status  Request Failed: {response.status_code, response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error in add_admin: {str(e)}")
            return None

    def update_network_status(self):
        try:
            connected_status = self.apiClient.put_request(update_network_status_connected)

            if connected_status.status_code == 200:
                self.logger.info(f"PUT network_status Request Successful: {connected_status.text}")

                return json.loads(connected_status.text)
            else:
                self.logger.info(f"PUT Request Failed: {connected_status.status_code, connected_status.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error in update_network_status: {str(e)}")
            return None


    def send_network_status(self, user_status,):
        try:
            if user_status:
                message_json = json.dumps({
                    "receiver": 'Admin',
                    "role": 'User',
                    "msg": SEND_NETWORK_STATUS,
                    "node_id": self.id,
                    "network_status": user_status['network_status']
                })
                self.mqtt_obj.send_internal_messages(message_json)

        except Exception as e:
            self.logger.error(f"Error in send_network_status: {str(e)}")

    def update_training_status(self):
        try:
            training_status = self.apiClient.put_request(toggle_training_status)

            if training_status.status_code == 200:
                self.logger.info(f"PUT training_status Request Successful: {training_status.text}")
                return json.loads(training_status.text)
            else:
                self.logger.error(f"PUT Request Failed: {training_status.status_code, training_status.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error in update_training_status: {str(e)}")
            return None

    def send_training_status(self, user_status,):
        try:
            if user_status:
                message_json = json.dumps({
                    "receiver": 'Admin',
                    "role": 'User',
                    "msg": SEND_TRAINING_STATUS,
                    "node_id": self.id,
                    "training_status": user_status['training_status']
                })
                self.mqtt_obj.send_internal_messages(message_json)

        except Exception as e:
            self.logger.error(f"Error in send_training_status: {str(e)}")

    def send_model_to_internal_cluster(self, user_status, hash,training_name, accuracy, loss):
        
        try:
            if user_status:
                message_json = json.dumps({
                    "receiver": 'Admin',
                    "msg": RECEIVE_MODEL_INFO,
                    "node_id": self.id,
                    "model_hash": hash,
                    "training_name":training_name,
                    "accuracy": accuracy,
                    "loss": loss

                })
                self.mqtt_obj.send_internal_messages(message_json)

        except Exception as e:
            self.logger.error(f"Error in send_model_to_internal_cluster: {str(e)}")

    def process_received_message(self, data):
        try:
            if isinstance(data, str):
                message_data = json.loads(data)
            elif isinstance(data, bytes):
                message_data = json.loads(data.decode('utf-8'))
            else:
                message_data = data.get()

            msg_type = message_data.get("msg")

            if msg_type == SEND_GLOBAL_MODEL_HASH:
                global_model = message_data.get("global_hash")
                self.handle_global_model(global_model)                
            elif msg_type == PAUSE_API:
                self.handle_pause_training(message_data)
            elif msg_type == RESUME_API:
                self.handle_resume_training(message_data)
            elif msg_type == TERMINATE_API:
                self.handle_terminate(message_data)

        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding JSON: {e}")
        except Exception as e:
            self.logger.error(f"Error in process_received_message: {str(e)}")


    
    def handle_global_model( self,global_model) :
        
        self.logger.info(f" got global model hash: {global_model}")

        db_data = {
                "global_model_hash": global_model
            }
        self.update_global_model(db_data)
        self.ml_operations.is_global_model_hash(global_model)
        self.logger.debug("Successfully Set global model hash")
        pass

    def handle_pause_training(self,message_data):
        node_id=message_data.get("node_id")
        if node_id==self.id:
            self.pause_training = True
            self.logger.debug(f" got pause training command: {message_data} and paused: {self.pause_training}")
            operation_statuss={
                "operation_status": "pause"
                }
            self.update_operation_status(operation_statuss)
        else :
            self.logger.debug(f"id {self.id} is not same as node_id : {node_id}")
        # pass

    def handle_resume_training(self,message_data ):
        node_id=message_data.get("node_id")

        if node_id==self.id:

            self.pause_training = False
            operation_statuss={
                "operation_status": "resume"
                }
            self.update_operation_status(operation_statuss)
            self.logger.debug(f" got resume training command: {message_data} and paused: {self.pause_training}")
        else :

            self.logger.debug(f"id {self.id} is not same as node_id : {node_id}")
            pass

    def handle_terminate(self,message_data):
        node_id=message_data.get("node_id")

        if node_id==self.id:
            self.logger.debug(f" got pause terimate command: {message_data}")
            operation_statuss={
                "network_status": "disconnected",
                "operation_status": "terminate"
                
                }
            self.update_operation_status(operation_statuss)

            self.mqtt_obj.terimate_connection()
            self.logger.debug("Terminate Successfully!!!!!")
            import sys
            sys.exit(0)     
        # else :
        #     self.logger.debug(f"id {self.id} is not same as node_id : {node_id}")
       
        # pass
