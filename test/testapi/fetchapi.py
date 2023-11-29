import requests

def fetch_results(url):
    try:
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Assuming the response contains JSON data, you can access it using response.json()
            data = response.json()
            
            # Process the data as needed
            print("Fetched data:", data)
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    api_url = "http://127.0.0.1:8000/api/v1/get-training-results/"
    fetch_results(api_url)
