import pytest
from Model.deepLearningModel.ANN import ANNTabularClassification



@pytest.fixture
def tabular_classification_model():
    return ANNTabularClassification('adam', log="test_classification_logs")

def test_train_and_evaluate_classification(tabular_classification_model):
    tabular_classification_model.train_model(epochs=1, batch_size=32)
    test_loss, test_accuracy = tabular_classification_model.evaluate_model()

    assert test_loss >= 0.0
    assert test_accuracy >= 0.0

def test_save_and_load_classification(tabular_classification_model):
    model_filename = 'classification_model.h5'
    tabular_classification_model.save_model(model_filename)

    assert tabular_classification_model.model is not None

    # Clean up the saved model file
    import os
    os.remove(model_filename)

def test_set_weights_classification(tabular_classification_model):
    # Save the initial weights
    initial_weights = tabular_classification_model.model.get_weights()

    # Create a new model with the same architecture
    new_model = ANNTabularClassification('adam', log="test_classification_logs")

    # Set the weights of the new model to the initial weights
    new_model.set_weights(initial_weights)

    # Ensure the weights are set correctly
    new_weights = new_model.model.get_weights()
    assert len(initial_weights) == len(new_weights)
    for i in range(len(initial_weights)):
        assert (initial_weights[i] == new_weights[i]).all()

def test_tensorboard_classification(tabular_classification_model):
    tabular_classification_model.run_tensorboard()

if __name__ == '__main__':
    pytest.main()
