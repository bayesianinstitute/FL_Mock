import pytest
import os
from Model.timeSeriesModel.RNN import TimeSeriesRNN
import numpy as np
from config.optimizer_settings import optimizers

# Define a fixture to create an instance of the TimeSeriesRNN class
@pytest.fixture(params=optimizers)  # Add optimizer, epochs, and batch_size combinations
def rnn_model(request):
    optimizer = request.param
    model = TimeSeriesRNN(
        ticker="AAPL",
        start_date="2022-01-01",
        end_date="2023-01-01",
        sequence_length=10,
        num_units=64,
        optimizer=optimizer,
        log_dir='custom_RNN_logs'
    )
    return model

# Test case to check if the RNN model can be created
def test_create_rnn_model(rnn_model):
    assert isinstance(rnn_model, TimeSeriesRNN)

# Test case to check if the RNN model can be trained
def test_train_rnn_model(rnn_model):
    # The model has already been trained in the fixture
    rnn_model.train_model(epochs=1, batch_size=32)

# Test case to check if the RNN model can be evaluated
def test_evaluate_rnn_model(rnn_model):
    mse, mape = rnn_model.evaluate_model()
    assert mse >= 0.0
    assert mape >= 0.0

# Test case to check if the RNN model can make forecasts
def test_forecast_rnn(rnn_model):
    input_data = rnn_model.data
    forecast = rnn_model.forecast(input_data)
    assert isinstance(forecast, np.ndarray)

# # Test case to check if weights can be set and retrieved
# def test_set_and_get_weights(rnn_model):
#     # Get the initial model weights
#     initial_weights = rnn_model.model.get_weights()

#     # Create a new instance
#     new_rnn_model = TimeSeriesRNN()
    
#     # Check if the weights of the new instance match the initial weights
#     new_weights = new_rnn_model.model.get_weights()
    
#     # Ensure the shapes of the weights match
#     assert len(initial_weights) == len(new_weights)
    
#     # Iterate through the weight arrays to verify their equality
#     for i in range(len(initial_weights)):
#         assert np.array_equal(initial_weights[i], new_weights[i])

if __name__ == '__main__':
    pytest.main()
