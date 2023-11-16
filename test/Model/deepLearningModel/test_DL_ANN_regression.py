
import pytest
from core.MLOPS.Model.deepLearningModel.ANN import ANNTabularLinearRegression

from config.optimizer_settings import optimizers

import os
import numpy as np

# Define a fixture to create an instance of the ANNTabularLinearRegression class
@pytest.fixture(params=optimizers)
def ann_model(request):
    model = ANNTabularLinearRegression(optimizer=request.param)
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


def test_evaluate_model(ann_model):

    test_loss, test_mae = ann_model.evaluate_model()
    assert test_loss >= 0.0
    assert test_mae >= 0.0



def test_set_weights(ann_model):
    # Test the set_weights method
    weights = ann_model.model.get_weights()
    new_model = ann_model.set_weights(weights)
    assert new_model is not None

@pytest.mark.skip()
def test_run_tensorboard():
    ann_classifier = ANNTabularLinearRegression()
    ann_classifier.run_tensorboard()

if __name__ == '__main__':
    pytest.main()