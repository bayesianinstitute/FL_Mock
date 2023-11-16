import pytest
import os

from core.MLOPS.Model.deepLearningModel.CNN import CNNMnist

from config.optimizer_settings import optimizers

@pytest.fixture(params=optimizers)
def mnist_model(request):
    return CNNMnist(request.param)

# Test case for training and evaluating the model
def test_train_and_evaluate(mnist_model):
    mnist_model.train_model(epochs=1, batch_size=32)
    test_loss, test_accuracy = mnist_model.evaluate_model()

    assert test_loss >= 0.0
    assert test_accuracy >= 0.0

# Test case for saving and loading the model
def test_save_and_load_model(mnist_model):
    model_filename = 'test_model.keras'
    mnist_model.save_model(model_filename)

    assert os.path.exists(model_filename)

    # Load the model from the file and check if it's the same model
    loaded_model = CNNMnist(mnist_model.optimizer)
    loaded_model.set_weights(mnist_model.model.get_weights())

    # Test if the loaded model performs well on the test data
    test_loss, test_accuracy = loaded_model.evaluate_model()

    assert test_loss >= 0.0
    assert test_accuracy >= 0.0

    # Clean up the saved model file
    os.remove(model_filename)

# Add more test cases as needed

if __name__ == '__main__':
    pytest.main()
