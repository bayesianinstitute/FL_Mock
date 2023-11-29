import paho.mqtt.client as mqtt
import requests
import json

def fetch_results(url):
    try:
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Assuming the response contains JSON data, you can access it using response.json()
            data = response.json()
            
            # Process the data as needed
            return data
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    api_url = "http://127.0.0.1:8000/api/v1/get-training-results/"
    fetch_data = fetch_results(api_url)
    # Extract the first (and only) element from the array
    data = fetch_data[0]
    main_data = json.dumps({
        "data": data
    })
    print("Fetched data:", main_data)

    # MQTT callback for when a message is received
    def on_message(client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        print(f"Received message: {payload}")


    mqtt_broker_address = 'test.mosquitto.org'
    mqtt_topic_publish = 'your_topic_subscribe'

        # MQTT client setup
    client = mqtt.Client()
    client.on_message = on_message
    
    # Connect to the MQTT broker
    client.connect(mqtt_broker_address, 1883, 60)

    client.subscribe(mqtt_topic_publish,qos=1)

    # Publish data to MQTT topic
    client.publish(mqtt_topic_publish, payload=main_data, qos=1, retain=False)

    try:
        # Keep the script running
        while True:
            pass
    except KeyboardInterrupt:
        # Disconnect from the MQTT broker on keyboard interrupt
        client.loop_stop()
        client.disconnect()

    print("Script terminated.")

    # Disconnect from the MQTT broker
    client.disconnect()
    print("Data published to MQTT topic.")
