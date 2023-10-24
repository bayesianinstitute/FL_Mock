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

    def run(self,cluster_name,internal_cluster_topic,id):
        get_list=None

        mqtt_obj=self.mqtt_operations.start_dfl_using_mqtt(internal_cluster_topic,cluster_name,id)
        #self.global_ipfs_link = self.utils.get_global_ipfs_link()
        mqtt_obj.subscribe_to_internal_messages()
        # mqtt_obj.get_head_node()
        self.pause_execution()

        while True:
            hash=self.ml_operations.train_machine_learning_model()
            print("hash: {}".format(hash))
            self.pause_execution()
            mqtt_obj.send_internal_messages_model(hash)


            self.pause_execution()
            mqtt_obj.receive_internal_messages()
            self.pause_execution()

            if (mqtt_obj.send_model_hash())==False:
                continue
            else :
                get_list=mqtt_obj.send_model_hash()
                self.ml_operations.aggregate_models(get_list)

                self.pause_execution()



   

            self.pause_execution()
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
