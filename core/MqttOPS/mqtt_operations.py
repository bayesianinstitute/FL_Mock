from core.MqttOPS.mqttCluster import MQTTCluster
from core.Logs_System.logger import Logger
from core.API.endpoint import *
class MqttOperations:
    def __init__(self,ip,internal_cluster_topic,initial_broker):
        self.ip=ip
        
        self.logger=Logger(name='MqttOPS_logger',api_endpoint=f"{self.ip}:8000/{update_logs}").get_logger()
        self.internal_cluster_topic=internal_cluster_topic
        self.initial_broker=initial_broker
        self.cluster=None

    

    def start_dfl_using_mqtt(self,role):
        try:
            self.cluster = MQTTCluster(self.ip,self.initial_broker,
                                       self.internal_cluster_topic,  role)
            
            receiver=None
            if role=='Admin':
                receiver='User'
            elif role=='User':
                receiver='Admin'    
            self.cluster.connect_clients(role,receiver)
            self.logger.info("Started DFL Process")
            return self.cluster
        except Exception as e:
            self.logger.error(f"Error in start_dfl_using_mqtt: {e}")
            return None

    def head_node_id(self):
        try:
            return self.cluster.get_head_node_id()
        except Exception as e:
            self.logger.error(f"Error in head_node_id: {e}")
            return None

    def winner_becomes_aggregator(self):
        try:
            head_node = self.cluster.get_head_node()
            return f"Winner node became the aggregator and node is {head_node}"
        except Exception as e:
            self.logger.error(f"Error in winner_becomes_aggregator: {e}")
            return None
    
