import sys
# from participant_identification import ParticipantIdentification
from mqtt_operations import MqttOperations
from ml_operations import MLOperations
from utils import Utils
import argparse
from testt.identify.testidentify import IdentifyParticipant



class DFLWorkflow:
    def __init__(self, broker_service, global_cluster_topic, internal_cluster_topic, id):
        self.global_ipfs_link = None
        self.participant_identification = None
        self.broker_service = broker_service
        self.internal_cluster_topic = internal_cluster_topic
        self.global_cluster_topic = global_cluster_topic
        self.mqtt_operations = None
        self.ml_operations = MLOperations()
        self.utils = Utils()
        self.global_model = None

        self.id = id
        self.is_status=None




    def pause_execution(self,):
        if input("Press Enter to continue (or type 'q' and press Enter to quit): ").strip().lower() == 'q':
            sys.exit()

    def run(self,):
        get_list=None
        self.participant = IdentifyParticipant(self.id,self.broker_service)
        self.is_status=self.participant.main()
        print("is worker head ",self.is_status)
        Num=3

        self.mqtt_operations = MqttOperations(self.internal_cluster_topic,self.global_cluster_topic,self.broker_service,Num,self.is_status,self.id)


        mqtt_obj=self.mqtt_operations.start_dfl_using_mqtt()
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
                print("Send global model")
                self.pause_execution()

                self.global_model=self.ml_operations.aggregate_models(get_list)
                print(" got Global model hash: {}".format(self.global_model))

                self.pause_execution()
                print(self.ml_operations.send_global_model_to_others(mqtt_obj,self.global_model))
                self.pause_execution()
            
            

            if self.is_status==False:
                global_model_hash=mqtt_obj.global_model()
                print("i am not aggregator got global model hash: {}".format(global_model_hash))
                self.ml_operations.is_global_model_hash(global_model_hash)

                


            if self.ml_operations.is_model_better():
                continue
            else:
                break

        print(self.ml_operations.post_training_steps())
        if self.ml_operations.aggregator_saves_global_model_in_ipfs():
            print(self.ml_operations.aggregator_saves_global_model_in_ipfs())
        self.pause_execution()

        print(self.mqtt_operations.disconnect())
        self.pause_execution()

        print(self.ml_operations.cleanup())
        self.pause_execution()

        if self.ml_operations.aggregator_stops_mqtt_broker_service():
            print(self.ml_operations.aggregator_stops_mqtt_broker_service())
        self.pause_execution()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("broker_service",help="Name of broker service")
    parser.add_argument("cluster_name", help="Name of the cluster")
    parser.add_argument("internal_cluster_topic", help="internal Cluster topic")
    parser.add_argument("id", help="client_id")

    args = parser.parse_args()

    workflow = DFLWorkflow(args.broker_service,args.cluster_name,args.internal_cluster_topic,args.id)

    workflow.run()
