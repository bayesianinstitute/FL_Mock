import json


def extract_endpoints(api_json):
    endpoints = []

    try:
        if 'item' in api_json:
            for item in api_json['item']:
                if 'request' in item and 'url' in item['request']:
                    raw_url = item['request']['url']['raw']
                    v1_index = raw_url.find('/v1/')
                    if v1_index != -1:
                        path = raw_url[v1_index + 4:]
                        endpoints.append(path)

        return endpoints
    except KeyError as e:
        print(f"KeyError: {e}")
        print("Unexpected JSON structure. Please check the JSON data.")
        return None


# Open the file and load JSON data
with open('Bayes.postman_collection.json', 'r') as file:
    json_data = json.load(file)
# Using the function to extract endpoints
endpoints = extract_endpoints(json_data)

# Print the extracted endpoints
for endpoint in endpoints:
    print(endpoint)
