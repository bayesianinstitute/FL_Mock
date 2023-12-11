import paho.mqtt.client as mqtt
import time
import json
import psutil
from core.Logs_System.logger import Logger

class IdentifyParticipant:
    def __init__(self, id,broker,ram_topic,aggregator_topic,minimum_participate):
        self.logger=Logger(name='identify-Participant').get_logger()
        self.broker = broker
        self.id=id
        self.computer_info = self.get_computer_info()
        self.participant_id = f"Machine-id-{self.id}"
        self.client = mqtt.Client(client_id=self.participant_id, userdata={"id":id,"ram_usages": {}, "shared_count": 0})
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, 1883)
        self.client.loop_start()
        self.aggregator = False 
        self.ram_topic=ram_topic
        self.aggregator_topic=aggregator_topic
        self.minimum_participate=minimum_participate
        
    def get_computer_info(self):
        try:
            ram = psutil.virtual_memory()
            used_ram = ram.used
            total_ram = ram.total
            available_ram = ram.available

            self.logger.info(f"Used RAM: {used_ram / (1024 ** 3):.2f} GB")
            self.logger.info(f"Total RAM: {total_ram / (1024 ** 3):.2f} GB")
            self.logger.info(f"Available RAM: {available_ram / (1024 ** 3):.2f} GB")

            return {"ram": available_ram}
        except Exception as e:
            self.logger.error(f"Error fetching computer info: {e}")
            return {"ram": 0} 

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            client.subscribe(self.ram_topic)
            client.subscribe(self.aggregator_topic)
        else:
            self.logger.error("Unable to connect to Broker. Result code: {}".format(rc))

    def on_message(self, client, userdata, message):
        try:
            ram_info = json.loads(message.payload.decode("utf-8"))
            node_id = ram_info.get("node_id")
            ram_usage = int(ram_info.get("ram_usage", 0))

            if node_id and ram_usage:
                if node_id not in userdata["ram_usages"]:
                    self.logger.info(f"Received RAM usage from {node_id}: {ram_usage} MB")
                    userdata["ram_usages"][node_id] = ram_usage
                    userdata["shared_count"] += 1
                else:
                    if userdata["ram_usages"][node_id] != ram_usage:
                        self.logger.info(f"Received RAM usage from {node_id}: {ram_usage} MB")
                        userdata["ram_usages"][node_id] = ram_usage

        except json.decoder.JSONDecodeError as e:
            self.logger.error(f"Received an invalid JSON message from {message.topic}: {e}")

    def announce_ram_usage(self):
        try:
            ram_usage = self.computer_info.get("ram", 0)
            ram_info = {"node_id": self.participant_id, "ram_usage": ram_usage}
            time.sleep(4)
            self.client.publish(self.ram_topic, json.dumps(ram_info), qos=1)
        except Exception as e:
            self.logger.error(f"Error announcing RAM usage: {e}")

    def declare_aggregator(self):
        try:
            aggregator_message = f"Machine {self.participant_id} is the aggregator!"
            self.client.publish(self.aggregator_topic, aggregator_message, qos=1)
        except Exception as e:
            self.logger.error(f"Error declaring aggregator: {e}")

    def is_highest_ram_usage(self, current_ram_usage):
        try:
            other_ram_usages = self.client._userdata.get("ram_usages", {})
            self.logger.info("other_ram_usages: ", other_ram_usages)
            return all(current_ram_usage >= ram_usage for ram_usage in other_ram_usages.values())
        except Exception as e:
            self.logger.error(f"Error checking RAM usage: {e}")
            return False

    def main(self):
        try:
            self.logger.info(f"My ID: {self.participant_id}")

            while True:
                self.announce_ram_usage()

                shared_count = self.client._userdata.get("shared_count", 0)

                if shared_count < self.minimum_participate:
                    self.logger.debug(f"Waiting for {self.minimum_participate - shared_count} more machine(s) to start the process...")
                else:
                    ram_usage = self.computer_info.get("ram", 0)
                    if self.is_highest_ram_usage(ram_usage):
                        self.declare_aggregator()
                        self.logger.info(f"I am the aggregator! RAM usage: {ram_usage} GB")
                        self.aggregator = True
                        return self.aggregator
                    else:
                        self.logger.info("I am not the aggregator")
                        return self.aggregator
        except Exception as e:
            self.logger.error(f"Error in main block: {e}")
            return False


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("id", help="client_id")

    args = parser.parse_args()

    broker='broker.hivemq.com'
    ram_topic="ram_topicc"
    declare_winner_topic="aggregator_topicc"
    Minimum_participate=5

    participant = IdentifyParticipant(args.id,broker,ram_topic,declare_winner_topic,Minimum_participate)
    status=participant.main()
