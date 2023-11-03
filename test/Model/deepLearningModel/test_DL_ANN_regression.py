
import pytest
from Model.deepLearningModel.ANN import ANNTabularLinearRegression

from config.optimizer_settings import optimizers

import os
import numpy as np

# Define a fixture to create an instance of the ANNTabularLinearRegression class
@pytest.fixture(optimizers)
def ann_model(request):
    model = ANNTabularLinearRegression(optimizer=request.params)
    return model

# Test case to check if the model can be created
def test_create_ann_model(ann_model):
    assert isinstance(ann_model, ANNTabularLinearRegression)

# Test case to check if the model can be trained
def test_train_ann_model(ann_model):
    ann_model.train_model(epochs=1, batch_size=32)

# Test case to check if the model can be evaluated
def test_evaluate_ann_model(ann_model):
    test_loss, test_mae = ann_model.evaluate_model()
    assert test_loss >= 0.0
    assert test_mae >= 0.0

# Test case to check if the model can be saved and loaded
def test_save_and_load_ann_model(ann_model):
    model_filename = 'test_ann_model.h5'
    ann_model.save_model(model_filename)
    assert os.path.exists(model_filename)

    loaded_model = ANNTabularLinearRegression()
    loaded_model.load_model(model_filename)

    test_loss, test_mae = loaded_model.evaluate_model()
    assert test_loss >= 0.0
    assert test_mae >= 0.0

    # Clean up the saved model file
    os.remove(model_filename)

# Test case to check if weights can be set and retrieved
def test_set_and_get_weights(ann_model):
    # Get the initial model weights
    initial_weights = ann_model.model.get_weights()

    # Create a new instance and set its weights
    new_ann_model = ANNTabularLinearRegression()
    new_ann_model.set_weights(initial_weights)

    # Check if the weights of the new instance match the initial weights
    new_weights = new_ann_model.model.get_weights()
    assert np.all(np.array(initial_weights) == np.array(new_weights))

if __name__ == '__main__':
    pytest.main()