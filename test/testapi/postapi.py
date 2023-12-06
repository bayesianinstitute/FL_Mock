import requests

url = "http://127.0.0.1:8000/api/v1/create_training_result/"

data = {
    "accuracy":1,
    "training_accuracy": 1,
    "validation_accuracy": 1,
    "loss": 1,
    "training_info": 1
}

headers = {
    "Content-Type": "application/json"
}

# Sending a POST request to the API endpoint
response = requests.post(url, json=data, headers=headers)

# Check the response
if response.status_code == 201:  # Assuming 201 means successful creation
    print("Data added successfully.")
else:
    print(f"Failed to add data. Status code: {response.status_code}")
    print(response.text)
