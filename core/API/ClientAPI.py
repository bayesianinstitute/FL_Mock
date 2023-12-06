import requests

class ApiClient:
    def __init__(self, base_url='http://127.0.0.1:8000/api/v1'):
        self.base_url = base_url

    def get_request(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        return response

    def post_request(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        print(data)
        response = requests.post(url, json=data, headers=headers)
        return response

    def put_request(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(url, data=data)
        return response

if __name__ == '__main__':
    # Example usage:
    base_url = "http://127.0.0.1:8000/api/v1"

    # Create an instance of the API client
    api_client = ApiClient(base_url)

    # Example GET request
    get_response = api_client.get_request(endpoint="get-track-role/", )
    if get_response.status_code == 200:
        print("GET Request Successful:", get_response.text)
    else:
        print("GET Request Failed:", get_response.status_code, get_response.text)

    # data = {
    #     "model_name": "ANN",
    #     "dataset_name": "Mnist",
    #     "optimizer": "Adam",
    #     "training_name": "USA"
    # }

    # # Example POST request
    # post_response = api_client.post_request(endpoint="create-training-information/", data=data)
    # if post_response.status_code == 201:
    #     print("POST Request Successful:", post_response.text)
    # else:
    #     print("POST Request Failed:", post_response.status_code, post_response.text)

    # # Example PUT request
    # put_response = api_client.put_request(endpoint='update-admin/')
    # if put_response.status_code == 200:
    #     print("PUT Request Successful:", put_response.text)
    # else:
    #     print("PUT Request Failed:", put_response.status_code, put_response.text)
