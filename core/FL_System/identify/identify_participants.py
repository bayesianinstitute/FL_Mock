import paho.mqtt.client as mqtt
import time
import json
import psutil

class IdentifyParticipant:
    def __init__(self, id,broker,ram_topic,aggregator_topic,minimum_participate):
        self.broker = broker
        self.id=id
        self.computer_info = self.get_computer_info()
        self.participant_id = f"Machine-id-{self.id}"
        self.client = mqtt.Client(client_id=self.participant_id, userdata={"id":id,"ram_usages": {}, "shared_count": 0})
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, 1883)
        self.client.loop_start()
        self.aggregator = False  # Initialize as non-aggregator
        self.ram_topic=ram_topic
        self.aggregator_topic=aggregator_topic
        self.minimum_participate=minimum_participate

    def get_computer_info(self):

        ram = psutil.virtual_memory()
        used_ram = ram.used
        total_ram = ram.total
        # Get available RAM
        available_ram = ram.available

        print(f"Used RAM: {used_ram / (1024 ** 3):.2f} GB")
        print(f"Total RAM: {total_ram / (1024 ** 3):.2f} GB")
        print(f"Available RAM: {available_ram / (1024 ** 3):.2f} GB")
        return {"ram": available_ram}

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to Broker")
            client.subscribe(self.ram_topic)
            client.subscribe(self.aggregator_topic)
        else:
            print("Unable to connect to Broker result code: {}".format(rc))

    def on_message(self, client, userdata, message):
        try:
            ram_info = json.loads(message.payload.decode("utf-8"))
            node_id = ram_info["node_id"]
            ram_usage = int(ram_info["ram_usage"])
            print(f"Received RAM usage from {node_id}: {ram_usage} GB")
            userdata["ram_usages"][node_id] = ram_usage
            userdata["shared_count"] += 1
        except json.decoder.JSONDecodeError:
            print(f"Received an invalid JSON message from {message.topic}: {message.payload}")

    def announce_ram_usage(self):

        ram_usage = self.computer_info["ram"]
        ram_info = {
            "node_id": self.participant_id,
            "ram_usage": ram_usage
        }
        time.sleep(10)
        self.client.publish(self.ram_topic, json.dumps(ram_info), qos=1)

    def declare_aggregator(self):
        aggregator_message = f"Machine {self.participant_id} is the aggregator!"

        self.client.publish(self.aggregator_topic, aggregator_message,qos=1)

    def is_highest_ram_usage(self, current_ram_usage):
        # Check if current_ram_usage is higher than any other participant's RAM usage
        other_ram_usages = self.client._userdata["ram_usages"]
        print("other_ram_usages :  ",other_ram_usages)
        return all(current_ram_usage >= ram_usage for ram_usage in other_ram_usages.values())

    def main(self):
        print("My ID:", self.participant_id)

        # Track the messages received from other participants
        messages_received = 0

        while True:
            self.announce_ram_usage()
            
            print(f"id ",self.client._userdata.get("id")," particpate id", self.participant_id)

            if self.id != self.participant_id:  # Fix the comparison
                    print("Received message")
                    time.sleep(5) # Adjust the sleep time as needed
                    messages_received += 1

            shared_count = messages_received  # Update shared_count based on received messages

            if shared_count < self.minimum_participate - 1:  # Subtract 1 to exclude self
                print(f"Waiting for {self.minimum_participate - 1 - shared_count} more machine(s) to start the process...")
            else:
                ram_usage = self.computer_info["ram"]
                if self.is_highest_ram_usage(ram_usage):
                    self.declare_aggregator()
                    print(f"I am the aggregator! RAM usage: {ram_usage} GB")
                    self.aggregator = True
                    return self.aggregator
                else:
                    print("I am not the aggregator")
                    return self.aggregator


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("id", help="client_id")

    args = parser.parse_args()

    broker='broker.hivemq.com'
    ram_topic="ram_topicc"
    declare_winner_topic="aggregator_topicc"
    Minimum_participate=3

    participant = IdentifyParticipant(args.id,broker,ram_topic,declare_winner_topic,Minimum_participate)
    status=participant.main()

    print("Status : " , status)