from flask import Flask, render_template, request, redirect, url_for
from main import DFLWorkflow
import json

app = Flask(__name__)

# Define the route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define the /train API route
@app.route('/train', methods=['POST'])
def train():
    company_name = request.form['companyName']
    model_name = request.form['modelName']
    dataset_name = request.form['datasetName']
    optimizer_name = request.form['optimizerName']
    num_clusters = request.form['numClusters']
    num_computers = request.form['numComputers']

    data = {
        "company_name": company_name,
        "model_name": model_name,
        "dataset_name": dataset_name,
        "optimizer_name": optimizer_name,
        "no_of_cluster": num_clusters,
        "no_of_computers": num_computers
    }

    # Write the JSON object to a file
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # You can define the parameters or configuration here or retrieve them from the request
    broker_service = "test.mosquitto.org"
    cluster_name = "USA"
    internal_cluster_topic = "internal_USA_topic"
    client_id = "1"
    min_node = 1  # Set your desired minimum node count

    # You can define the updated_broker here or retrieve it from the request
    updated_broker = 'broker.hivemq.com'

    # Create and run the DFLWorkflow
    voting_topic = f'Voting topic on Cluster {cluster_name}'
    declare_winner_topic = f'Winner Topic on Cluster {cluster_name}'

    workflow = DFLWorkflow(broker_service, cluster_name, internal_cluster_topic, client_id, voting_topic, declare_winner_topic, min_node, updated_broker,data["model_name"],optimizer_name)
    workflow.run()

    # After saving the data, redirect back to the home page
    return redirect(url_for('home'))

@app.route('/stop', methods=['POST'])
def stop_training():
    
    
    return "Training stop request sent"


if __name__ == '__main__':
    app.run(debug=True)
