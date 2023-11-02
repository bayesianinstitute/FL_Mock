from flask import Flask, render_template, request, redirect, url_for
from main import DFLWorkflow

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
    num_clusters = request.form['numClusters']
    num_computers = request.form['numComputers']

    # Save the form data to a text file in a specific directory
    with open('templates/data.txt', 'w') as file:
        file.write(f"Company Name: {company_name}\n")
        file.write(f"Model Name: {model_name}\n")
        file.write(f"Dataset Name: {dataset_name}\n")
        file.write(f"Number of Clusters: {num_clusters}\n")
        file.write(f"Number of Computers: {num_computers}\n")

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

    workflow = DFLWorkflow(broker_service, cluster_name, internal_cluster_topic, client_id, voting_topic, declare_winner_topic, min_node, updated_broker)
    workflow.run()

    # After saving the data, redirect back to the home page
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
