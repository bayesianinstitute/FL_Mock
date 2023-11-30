import requests

url = "http://127.0.0.1:8000/api/v1/update-admin/"

response = requests.put(url)

# Check the response
if response.status_code == 200:  # Assuming 201 means successful creation
    print("Data added successfully.")

else:
    print(f"Failed to add data. Status code: {response.status_code}")
    print(response.text)

