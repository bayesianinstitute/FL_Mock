import json
from core.API.endpoint import *
from core.Logs_System.logger import Logger

class User:
    def __init__(self, apiClient, ml_operations, mqtt_operations,logger):
        self.apiClient = apiClient
        self.ml_operations = ml_operations
        self.mqtt_operations = mqtt_operations
        self.logger = logger

    def user_logic(self, role_data, mqtt_obj):
        # Update connected Status
        connected_status = self.apiClient.put_request(network_connected_endpoint)
        if connected_status.status_code == 200:
            self.logger.info(f"PUT network_status Request Successful:{ connected_status.text}")
            user_status = json.loads(connected_status.text)
            message = "connection_status"
            message_json = json.dumps({
                "msg": message,
                "id": user_status['id'],
                "network_status": user_status['network_status']
            })
            mqtt_obj.send_internal_messages(message_json)
        else:
            self.logger.info(f"PUT Request Failed: {connected_status.status_code, connected_status.text}")

        # Update training Status
        training_status = self.apiClient.put_request(toggle_training_status_endpoint)
        if training_status.status_code == 200:
            self.logger.info(f"PUT training_status Request Successful:{ training_status.text}")
            user_status = json.loads(training_status.text)
            message = "training_status"
            message_json = json.dumps({
                "msg": message,
                "id": user_status['id'],
                "training_status": user_status['training_status'],
            })
            mqtt_obj.send_internal_messages(message_json)
        else:
            self.logger.error(f"PUT Request Failed: { training_status.status_code, training_status.text}")

        hash, accuracy, loss = self.ml_operations.train_machine_learning_model()
        self.logger.info(f"Model hash: {hash}")

        # TODO: Need post api to update the latest training model hash
        # Send the model to the internal cluster
        message_json = json.dumps({
            "client_id": user_status['id'],
            "model_hash": hash,
            "accuracy": accuracy,
            "loss": loss,
        })

        mqtt_obj.send_internal_messages_model(message_json)
        latest_global_model_hash = mqtt_obj.global_model()

        if latest_global_model_hash:
            # TODO: post api to add the latest global model hash
            self.logger.info(f"I am not aggregator, got global model hash: {latest_global_model_hash}")
            # Set the latest global model hash and set weights in MLOperation
            self.ml_operations.is_global_model_hash(latest_global_model_hash)
            mqtt_obj.global_model_hash = None

        # Temporary to close the program
