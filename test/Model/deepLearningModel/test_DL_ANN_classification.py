import pytest
from Model.deepLearningModel.ANN import ANNTabularClassification

# List of optimizers to test

from config.optimizer_settings import optimizers


@pytest.fixture(params=optimizers)
def ann_classifier(request):
    # Initialize the ANNTabularClassification with the specified optimizer
    return ANNTabularClassification(optimizer=request.param)

def test_build_model(ann_classifier):
    # Test the build_model method
    model = ann_classifier.build_model()
    assert model is not None

def test_train_model(ann_classifier):
    # Test the train_model method
    ann_classifier.train_model(epochs=2, batch_size=32)

def test_evaluate_model(ann_classifier):
    # Test the evaluate_model method
    loss, accuracy = ann_classifier.evaluate_model()
    assert isinstance(loss, float)
    assert isinstance(accuracy, float)

def test_save_model(ann_classifier):
    # Test the save_model method
    model_filename = "test_model.keras"
    ann_classifier.save_model(model_filename)
    # You can add additional assertions to check if the model file was created.

def test_set_weights(ann_classifier):
    # Test the set_weights method
    weights = ann_classifier.model.get_weights()
    new_model = ann_classifier.set_weights(weights)
    assert new_model is not None

# Run TensorBoard and test the run_tensorboard method (optional)
@pytest.mark.skip()
def test_run_tensorboard():
    ann_classifier = ANNTabularClassification()
    ann_classifier.run_tensorboard()

if __name__ == "__main__":
    pytest.main()
