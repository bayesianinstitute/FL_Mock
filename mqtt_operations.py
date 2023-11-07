from core.MqttCluster.mqttCluster import MQTTCluster

class MqttOperations:
    def __init__(self,internal_cluster_topic,global_cluster_topic,initial_broker,num_workers,status,id):
        # You can add any necessary initialization code here
        self.internal_cluster_topic=internal_cluster_topic
        self.global_cluster_topic = global_cluster_topic
        self.num_workers =num_workers
        self.initial_broker=initial_broker
        self.cluster=None
        self.cluster_name=global_cluster_topic
        self.status=status
        self.id=id

    

    def start_dfl_using_mqtt(self,):
        """
        This method represents the action taken to start distributed federated learning (DFL) using MQTT communication.

        Pseudocode:
        1. Initialize the DFL process.
        2. Configure DFL to use MQTT for communication.
        3. Start the DFL process using MQTT as the communication method.

        Returns:
         MQTTCluster Object for communication.
        """
        # Configuration and create 3 client


        self.cluster = MQTTCluster(self.initial_broker, self.num_workers, self.cluster_name, self.global_cluster_topic, self.internal_cluster_topic,self.status,self.id)

        # Create clients for  clusters
        self.cluster.create_clients()

        print(f'check head node {self.status}')

        print("Started DFL Process")

        return self.cluster

    def winner_becomes_aggregator(self):
        """
        This method represents the action taken when the winner node becomes the aggregator in the DFL process.

        Pseudocode:
        1. Check if the current node is the winner.
        2. If the current node is the winner:
            a. Assume the role of the aggregator.
        3. Return a message confirming that the winner node has become the aggregator.

        Returns:
        A message indicating that the winner node has assumed the role of the aggregator.
        """

        head_node=self.cluster.get_head_node() 
        return f"Winner node became the aggregator and node is {head_node}"
    
