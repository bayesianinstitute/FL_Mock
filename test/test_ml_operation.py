import pytest
from unittest.mock import Mock
from core.MLOPS.ml_operations import MLOperations
@pytest.fixture
def ml_operations():
    training_type = 'CNN'
    optimizer = 'adam'
    return MLOperations(training_type, optimizer)

@pytest.mark.skip("Skip MQTT-related functions")
def test_send_global_model_to_others(ml_operations):
    # Your test logic here
    pass

@pytest.mark.skip("Skip MQTT-related functions")
def test_send_model_to_aggregator(ml_operations):
    # Your test logic here
    pass

@pytest.mark.skip("Skip MQTT-related functions")
def test_aggregator_receives_models(ml_operations):
    # Your test logic here
    pass

def test_train_machine_learning_model(ml_operations):
    # Your test logic for training a machine learning model here
    hash1 = ml_operations.train_machine_learning_model()
    assert isinstance(hash1, str)  # Check if hash1 is a string
    return hash1  # Return the hash obtained from training

def test_aggregate_models(ml_operations, test_train_machine_learning_model):
    # Your test logic for aggregating models here
    model_list = [test_train_machine_learning_model,test_train_machine_learning_model]  # Pass the hash obtained from training
    global_model_hash = ml_operations.aggregate_models(model_list)
    assert isinstance(global_model_hash, str)  # Check if global_model_hash is a string

def test_aggregator_saves_global_model_in_ipfs(ml_operations):
    # Your test logic for saving the global model in IPFS here
    result = ml_operations.aggregator_saves_global_model_in_ipfs()
    assert result is True  # Check if the operation is successful

if __name__ == '__main__':
    pytest.main()