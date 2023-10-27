import paho.mqtt.client as mqtt
import time
import json
import psutil

class IdentifyParticipant:
    def __init__(self, id,):
        self.broker = 	'broker.hivemq.com'
        self.id=id
        self.computer_info = self.get_computer_info()
        self.participant_id = f"Machine-id-{self.id}"
        self.client = mqtt.Client(client_id=self.participant_id, userdata={"ram_usages": {}, "shared_count": 0})
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        # self.client.on_disconnect = self.on_disconnect
        self.client.connect(self.broker, 1883)
        self.client.loop_start()
        self.aggregator = False  # Initialize as non-aggregator

    def get_computer_info(self):
        # total_ram = psutil.virtual_memory().total / (1024 ** 3)  # RAM in GB
        return {"ram": self.id}

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to Broker")
            client.subscribe("ram_topic")
        else:
            print("Unable to connect to Broker result code: {}".format(rc))

    def on_message(self, client, userdata, message):
        ram_info = json.loads(message.payload.decode("utf-8"))
        node_id = ram_info["node_id"]
        ram_usage = int(ram_info["ram_usage"])
        print(f"Received RAM usage from {node_id}: {ram_usage} GB")
        userdata["ram_usages"][node_id] = ram_usage
        userdata["shared_count"] += 1

    def announce_ram_usage(self):
        topic = 'ram_topic'
        ram_usage = self.computer_info["ram"]
        ram_info = {
            "node_id": self.participant_id,
            "ram_usage": ram_usage
        }
        time.sleep(10)
        self.client.publish(topic, json.dumps(ram_info), qos=1,)

    def declare_aggregator(self):
        topic = 'aggregator_topic'
        aggregator_message = f"Machine {self.participant_id} is the aggregator!"
        # time.sleep(10)
        self.client.publish(topic, aggregator_message)

    def is_highest_ram_usage(self, current_ram_usage):
        # Check if current_ram_usage is higher than any other participant's RAM usage
        other_ram_usages = self.client._userdata["ram_usages"]
        print("other_ram_usages :  ",other_ram_usages)
        return all(current_ram_usage >= ram_usage for ram_usage in other_ram_usages.values())

    def main(self):
        print("My ID:", self.participant_id)

        self.announce_ram_usage()

        while True:
            shared_count = self.client._userdata["shared_count"]
            if shared_count < 3:
                time.sleep(4)  # Wait for more clients to share data
            else:
                # Check if this node has the highest RAM usage
                ram_usage = self.computer_info["ram"]
                if self.is_highest_ram_usage(ram_usage):
                    self.declare_aggregator()
                    print(f"I am the aggregator! RAM usage: {ram_usage} GB")
                    self.aggregator = True
                    self.client.disconnect()
                    return self.aggregator
                else:
                    print("I am not the aggregator")
                    self.client.disconnect()

                    return self.aggregator

            # time.sleep(10)  # Add a delay to avoid constantly checking

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("id", help="client_id")

    args = parser.parse_args()

    participant = IdentifyParticipant(args.id)
    status=participant.main()

    print("Status : " , status)