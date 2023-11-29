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
    data = fetch_results(api_url)

    main_data = json.dumps({
        "data": data
    })
    print("Fetched data:", data)

    # MQTT settings
    # MQTT callback for when a message is received
    def on_message(client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        print(f"Received message: {payload}")


    mqtt_broker_address = 'test.mosquitto.org'
    mqtt_topic_publish = 'your_topic_publish'

        # MQTT client setup
    client = mqtt.Client()
    client.on_message = on_message
    
    # Connect to the MQTT broker
    client.connect(mqtt_broker_address, 1883, 60)

    # Publish data to MQTT topic
    client.publish(mqtt_topic_publish, payload=main_data, qos=1, retain=False)

    # Disconnect from the MQTT broker
    client.disconnect()
    print("Data published to MQTT topic.")
