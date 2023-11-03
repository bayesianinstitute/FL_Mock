import pytest

from main import DFLWorkflow
# Define fixtures or setup code if needed

def test_dfl_workflow_initialization():
    # Test the initialization of the DFLWorkflow class
    workflow = DFLWorkflow(
        broker_service="test.mosquitto.org",
        global_cluster_topic="USA",
        internal_cluster_topic="internal_USA_topic",
        id="132f",
        voting_topic=f'Voting topic on Cluster USA ',
        declare_winner_topic=f'Winner Topic on Cluster USA',
        min_node=3,  # Set your desired min_node value
        updated_broker="broker.hivemq.com",
        training_type="CNN",
        optimizer="adam"
    )
    assert workflow is not None

def test_dfl_workflow_run():
    # Test the run method of the DFLWorkflow class
    workflow = DFLWorkflow(
        broker_service="test.mosquitto.org",
        global_cluster_topic="your_global_cluster_topic",
        internal_cluster_topic="your_internal_cluster_topic",
        id="your_id",
        voting_topic="your_voting_topic",
        declare_winner_topic="your_declare_winner_topic",
        min_node=3,  # Set your desired min_node value
        updated_broker="broker.hivemq.com",
        training_type="CNN",
        optimizer="adam"
    )
    workflow.run()  # Test if it runs without errors

# Add more test cases as needed

if __name__ == '__main__':
    pytest.main()
    
