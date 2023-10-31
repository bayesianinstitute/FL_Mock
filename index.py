from flask import Flask, request, render_template, jsonify
from main import DFLWorkflow

app = Flask(__name__, template_folder='templates')
workflow = DFLWorkflow()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_workflow', methods=['POST'])
def run_workflow():
    cluster_name = request.form.get('cluster_name')
    internal_cluster_topic = request.form.get('internal_cluster_topic')
    id = request.form.get('id')
    workflow.run(cluster_name, internal_cluster_topic, id)
    return jsonify({"message": "Workflow executed successfully"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
