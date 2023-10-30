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


        pass

    def winner_creates_mqtt_broker(self):
        """
        This method represents the action taken when the winner of the DFL process creates an MQTT broker.

        Pseudocode:
        1. Check if the current node is the winner.
        2. If the current node is the winner:
            a. Create an MQTT broker to facilitate communication.
        3. Return a message indicating that the MQTT broker has been created.

        Returns:
        A message confirming the creation of an MQTT broker by the winner node.
        """
        return "MQTT broker created by the winner"

    def send_communication_link_to_others(self):
        """
        This method represents the action taken when the winner sends a communication link to other participants.

        Pseudocode:
        1. Check if the current node is the winner.
        2. If the current node is the winner:
            a. Generate a communication link.
            b. Send the communication link to other participants in the DFL process.
        3. Return a message confirming the successful transmission of the communication link.

        Returns:
        A message confirming that the communication link has been sent to other participants.
        """
        return "Communication link sent to others"

    def receive_mqtt_broker_link(self):
        """
        This method represents the action taken when a participant receives the MQTT broker link from the winner.

        Pseudocode:
        1. Wait for the winner to send the MQTT broker link.
        2. Receive the MQTT broker link.
        3. Return a message indicating that the MQTT broker link has been received.

        Returns:
        A message confirming the reception of the MQTT broker link.
        """
        return "Received MQTT broker link"
    

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


        self.cluster = MQTTCluster(self.initial_broker, self.num_workers, self.cluster_name, self.global_cluster_topic, self.internal_cluster_topic,self.status)

        # Create clients for  clusters
        self.cluster.create_clients(self.id)

        # self.cluster.switch_worker_head_node()

        print(f' head node {self.status}')
        

        print("Started DFL Process")

        return self.cluster
    
    # def receive_message(self,internal_cluster_topic,cluster_name):
    #     self.cluster.sub

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
    
