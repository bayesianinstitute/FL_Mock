import paho.mqtt.client as mqtt
import time
import json
import random
import psutil

class IdentifyParticipant:
    def __init__(self, broker='test.mosquitto.org'):
        self.broker = broker
        self.participant_id = f"Machine-id-{random.randint(1, 1000)}"
        self.client = mqtt.Client(client_id=self.participant_id,userdata={"ram_usages": {}, "shared_count": 0})
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect=self.on_disconnect
        self.client.connect(self.broker, 1883)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe("ram_topic")

    def on_message(self, client, userdata, message):
        ram_info = json.loads(message.payload.decode("utf-8"))
        node_id = ram_info["node_id"]
        ram_usage = ram_info["ram_usage"]
        print(f"Received RAM usage from {node_id}: {ram_usage} MB")
        userdata["ram_usages"][node_id] = ram_usage
        userdata["shared_count"] += 1

    def announce_ram_usage(self):
        topic = 'ram_topic'
        ram_usage = self.measure_ram_usage()
        ram_info = {
            "node_id": self.participant_id,
            "ram_usage": ram_usage
        }
        self.client.publish(topic, json.dumps(ram_info), qos=1, retain=True)

    def declare_aggregator(self):
        topic = 'aggregator_topic'
        aggregator_message = f"Machine {self.participant_id} is the aggregator!"
        self.client.publish(topic, aggregator_message)

    def measure_ram_usage(self):
        try:
            ram_usage = psutil.virtual_memory().used / (1024 ** 2)  # Get RAM usage in MB
            print(f"ram_usage: {ram_usage} MB")
            return ram_usage
        except Exception as e:
            print(f"Error measuring RAM usage: {str(e)}")
            return 0  # Default to 0 if measurement fails

    def is_highest_ram_usage(self, current_ram_usage):
        # Check if current_ram_usage is equal to or higher than the highest RAM usage
        max_ram_usage = max(self.client._userdata["ram_usages"].values())
        return current_ram_usage >= max_ram_usage

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"Unexpected disconnection with result code {rc}")
        else:
            print("Disconnected successfully")

    def main(self):
        print("My ID:", self.participant_id)
        aggregator=False

        # Announce RAM usage
        self.announce_ram_usage()

        while True:
            shared_count = self.client._userdata["shared_count"]
            if shared_count < 1:
                time.sleep(10)  # Wait for more clients to share data
            else:
                # self.client.disconnect()  # Disconnect the client
                # Check if this node has the highest RAM usage
                ram_usage = self.measure_ram_usage()
                if self.is_highest_ram_usage(ram_usage):
                    self.declare_aggregator()
                    print(f"I am the aggregator! RAM usage: {ram_usage} MB")
                    aggregator = True  # Set aggregator status to True
                    time.sleep(10)  # Wait for others to process the message
                    self.client.disconnect()

                    return aggregator

                    

                    
                else:
                    print("I am not the aggregator")
                    return False

if __name__ == '__main__':
    participant = IdentifyParticipant()
    status=participant.main()
    print(status)