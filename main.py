import sys
from participant_identification import ParticipantIdentification
from mqtt_operations import MqttOperations
from ml_operations import MLOperations
from utils import Utils
import argparse


class DFLWorkflow:
    def __init__(self):
        self.global_ipfs_link = None
        self.participant_identification = ParticipantIdentification()
        self.mqtt_operations = MqttOperations()
        self.ml_operations = MLOperations()
        self.utils = Utils()

    def pause_execution(self,):
        if input("Press Enter to continue (or type 'q' and press Enter to quit): ").strip().lower() == 'q':
            sys.exit()

    def run(self,cluster_name,internal_cluster_topic):
        # print(self.participant_identification.identify_participants())
        # self.pause_execution()

        # if self.participant_identification.determine_winner():
        #     print(self.mqtt_operations.winner_creates_mqtt_broker())
        #     self.pause_execution()
        #     if self.mqtt_operations.send_communication_link_to_others():
        #         print(self.mqtt_operations.send_communication_link_to_others())
        #     else:
        #         print(self.mqtt_operations.receive_mqtt_broker_link())
        #     self.pause_execution()

        print(self.mqtt_operations.start_dfl_using_mqtt(internal_cluster_topic,cluster_name))
        #self.global_ipfs_link = self.utils.get_global_ipfs_link()
        print(self.mqtt_operations.winner_becomes_aggregator())
        self.pause_execution()

        while True:
            hash=self.ml_operations.train_machine_learning_model()
            self.pause_execution()
            print(self.mqtt_operations.send_model_to_aggregator(hash))


            self.pause_execution()
            # print(self.ml_operations.aggregator_receives_models())
            # self.pause_execution()
            # print(self.ml_operations.aggregate_models())
            # self.pause_execution()
            # print(self.ml_operations.send_global_model_to_others())
            self.pause_execution()

            if self.ml_operations.is_model_better():
                continue
            else:
                break

        print(self.ml_operations.post_training_steps())
        if self.ml_operations.aggregator_saves_global_model_in_ipfs():
            print(self.ml_operations.aggregator_saves_global_model_in_ipfs())
        self.pause_execution()

        print(self.ml_operations.disconnect_all_nodes())
        self.pause_execution()

        print(self.ml_operations.cleanup())
        self.pause_execution()

        if self.ml_operations.aggregator_stops_mqtt_broker_service():
            print(self.ml_operations.aggregator_stops_mqtt_broker_service())
        self.pause_execution()

if __name__ == "__main__":
    workflow = DFLWorkflow()
    parser = argparse.ArgumentParser()
    parser.add_argument("cluster_name", help="Name of the cluster")
    parser.add_argument("internal_cluster_topic", help="internal Cluster topic")
    parser.add_argument("id", help="client_id")

    args = parser.parse_args()
    workflow.run(args.cluster_name,args.internal_cluster_topic,args.id)
