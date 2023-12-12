import json
import time

from core.API.endpoint import *
from core.Role.MsgType import *

from core.API.ClientAPI import ApiClient
from core.MLOPS.ml_operations import MLOperations
from core.Logs_System.logger import Logger
class User:
    def __init__(self,training_name,training_type, optimizer,mqtt_operations,role='User'):
        self.apiClient=ApiClient()
        self.ml_operations = MLOperations(training_type, optimizer,training_name=f'{training_name}_client')
        self.logger = Logger(name='user-role').get_logger()
        self.pause_training = False
                        # Start, initialize, and get MQTT communication object
        self.mqtt_obj = mqtt_operations.start_dfl_using_mqtt(role)
        
    def user_logic(self,):
        rounds=0
        try:
            last_update_time = time.time()

            # send for first time
            user_status = self.update_network_status()
            self.send_network_status(user_status, )

            while True:
                current_time = time.time()

                # Check if 60 seconds have passed since the last update
                if current_time - last_update_time >= 30:
                    user_status = self.update_network_status()
                    self.send_network_status(user_status, )

                    # Update the last update time
                    last_update_time = current_time

                received_message = self.mqtt_obj.handle_user_data()
                if received_message:
                    self.process_received_message(received_message)

                if not self.pause_training:
                    rounds=rounds+1
                    
                    user_status = self.update_training_status() 
                    self.send_training_status(user_status,) 

                    hash,final_accuracy, final_loss,  _,_= self.ml_operations.train_machine_learning_model(rounds=rounds,epochs=5,batch_size=32)
                    self.logger.info(f"Model hash: {hash}")
                    self.send_model_to_internal_cluster(user_status, hash, final_accuracy, final_loss,rounds)
                    time.sleep(1)
        except Exception as e:
            self.logger.error(f"Error in user_logic: {str(e)}")
        
        
    def update_network_status(self):
        try:
            connected_status = self.apiClient.put_request(network_connected_endpoint)

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
                    "node_id": self.mqtt_obj.id,
                    "network_status": user_status['network_status']
                })
                self.mqtt_obj.send_internal_messages(message_json)

        except Exception as e:
            self.logger.error(f"Error in send_network_status: {str(e)}")

    def update_training_status(self):
        try:
            training_status = self.apiClient.put_request(toggle_training_status_endpoint)

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
                    "node_id": self.mqtt_obj.id,
                    "training_status": user_status['training_status'],
                })
                self.mqtt_obj.send_internal_messages(message_json)

        except Exception as e:
            self.logger.error(f"Error in send_training_status: {str(e)}")

    def send_model_to_internal_cluster(self, user_status, hash, accuracy, loss,rounds):
        
        try:
            if user_status:
                message_json = json.dumps({
                    "receiver": 'Admin',
                    "msg": RECEIVE_MODEL_INFO,
                    "node_id": self.mqtt_obj.id,
                    "model_hash": hash,
                    "accuracy": accuracy,
                    "loss": loss,
                    "training_round":rounds
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
            time.sleep(10)


    
    def handle_global_model( self,global_model) :
        
        self.logger.info(f" got global model hash: {global_model}")
        self.ml_operations.is_global_model_hash(global_model)
        self.logger.debug("Successfully Set global model hash")
        pass

    def handle_pause_training(self,message_data):
        self.pause_training = True
        self.logger.debug(f" got pause training command: {message_data} and paused: {self.pause_training}")
        pass

    def handle_resume_training(self,message_data ):
        self.pause_training = False

        self.logger.debug(f" got resume training command: {message_data} and paused: {self.pause_training}")
        pass

    def handle_terminate(self,message_data):
        self.logger.debug(f" got pause terimate command: {message_data}")
        self.mqtt_obj.terimate_connection()
        self.logger.debug("Terminate Successfully!!!!!")
        import sys

        sys.exit(0)

       
        pass
