import argparse
from core.MqttOPS.mqttCluster import MQTTCluster

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cluster_name", help="Name of the cluster")
    parser.add_argument("num_workers", help="Number of workers")
    parser.add_argument("internal_cluster_topic", help="internal Cluster topic")
    args = parser.parse_args()

    # Configuration
    global_cluster_topic = "inter-cluster-topic"
    broker="test.mosquitto.org"
    cluster = MQTTCluster(broker, int(args.num_workers), args.cluster_name, global_cluster_topic, args.internal_cluster_topic)

    # Create clients for  clusters
    cluster.create_clients()

    # Run the logic for cluster
    cluster.run()


