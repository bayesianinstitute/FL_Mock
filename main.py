import sys
from mqtt_operations import MqttOperations
from ml_operations import MLOperations
from utils import Utils
import argparse

from core.FL_System.identifyparticipants.identify_participants import IdentifyParticipant
import time
import uuid


class DFLWorkflow:
    def __init__(self,
                 broker_service,
                 global_cluster_topic,
                 internal_cluster_topic, 
                 id,voting_topic,
                 declare_winner_topic,
                 min_node,
                 updated_broker,
                 training_type,
                 optimizer,
        
                 ):
        self.global_ipfs_link = None
        self.participant_identification = None
        self.broker_service = broker_service
        self.internal_cluster_topic = internal_cluster_topic
        self.global_cluster_topic = global_cluster_topic
        self.mqtt_operations = None
        self.ml_operations = MLOperations(training_type,optimizer)
        self.utils = Utils()
        self.global_model = None

        self.voting_topic=voting_topic
        self.winner_declare=declare_winner_topic

        self.id =  f'{id}-{uuid.uuid4()}'
        self.is_status=None
        self.min_node=min_node
        self.updated_broker=updated_broker

    
    def terminate_program(self):
        print("Terminated program Successfully ")
        sys.exit()



    def pause_execution(self,):
        if input("Press Enter to continue (or type 'q' and press Enter to quit): ").strip().lower() == 'q':
            sys.exit()

    def run(self,):
        get_list=None
        self.participant = IdentifyParticipant(self.id,self.broker_service,self.voting_topic,self.winner_declare,self.min_node)
        self.is_status=self.participant.main()
        print("is worker head ",self.is_status)
        

        self.mqtt_operations = MqttOperations(self.internal_cluster_topic,
                                              self.global_cluster_topic,
                                              self.broker_service,
                                              self.min_node,
                                              self.is_status,
                                              self.id)


        mqtt_obj=self.mqtt_operations.start_dfl_using_mqtt()
        mqtt_obj.subscribe_to_internal_messages()

        Round_Counter=0

        while True:

            if mqtt_obj.terimate_status:
                self.terminate_program()




            Round_Counter=Round_Counter+1

            print("Round_Counter : ",Round_Counter )

            time.sleep(5)

            # if Round_Counter==2:
            #     print("Changing Broker")
            #     time.sleep(10)
            #     mqtt_obj.switch_broker(self.updated_broker)



            hash=self.ml_operations.train_machine_learning_model()
            print("hash: {}".format(hash))
            # self.pause_execution()
            mqtt_obj.send_internal_messages_model(hash)


            # self.pause_execution()
            mqtt_obj.receive_internal_messages()
            # self.pause_execution()


            # if head status is True send,aggreagte and send global model to all workers
            if self.is_status==True:
                get_list=mqtt_obj.send_model_hash()
                print("Send global model",get_list)
                # self.pause_execution()

                self.global_model=self.ml_operations.aggregate_models(get_list)
                print(" got Global model hash: {}".format(self.global_model))

                # self.pause_execution()
                print(self.ml_operations.send_global_model_to_others(mqtt_obj,self.global_model))
                # for key in mqtt_obj.client_hash_mapping:
                #     mqtt_obj.client_hash_mapping[key] = None
                mqtt_obj.client_hash_mapping.clear()
                print("clear all hash operations")

                global_model_hash=mqtt_obj.global_model()
                print("i am  aggregator here is the  global model hash: {}".format(global_model_hash))

                self.ml_operations.is_global_model_hash(global_model_hash)

                if Round_Counter==2:
                    print("terimating by user")
                    mqtt_obj.send_terimate_message("Terminate")

                    time.sleep(5)


                    self.terminate_program()




        
            else :
                global_model_hash=mqtt_obj.global_model()
                print("i am not aggregator got global model hash: {}".format(global_model_hash))

                self.ml_operations.is_global_model_hash(global_model_hash)
            
            if Round_Counter==6:
                break




        print(f"Training Completed with round {Round_Counter} !! ")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("broker_service",help="Name of broker service",type=str)
    parser.add_argument("cluster_name", help="Name of the cluster",type=str,)
    parser.add_argument("internal_cluster_topic", help="internal Cluster topic",type=str)
    parser.add_argument("id", help="client_id",type=str)
    parser.add_argument("min_node", help="minimun Node",type=int)

    # min_node = 3

    updated_broker= 'broker.hivemq.com'

    model_type='CNN'

    optimizer ='adam'

    # dataset='Mnist'
    
   

    args = parser.parse_args()

    voting_topic=f'Voting topic on Cluster {args.cluster_name}'

    declare_winner_topic=f'Winner Topic on Cluster {args.cluster_name}'


    workflow = DFLWorkflow(args.broker_service,args.cluster_name,args.internal_cluster_topic,args.id,voting_topic,declare_winner_topic,args.min_node,updated_broker,model_type,optimizer)

   # run using python main.py test.mosquitto.org USA internal_USA_topic --id 1 --min_node 3

    workflow.run()
