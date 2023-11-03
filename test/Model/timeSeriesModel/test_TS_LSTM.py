import pytest
import os
import numpy as np
from Model.timeSeriesModel.LSTM import TimeSeriesLSTM
from config.optimizer_settings import optimizers

# Define a fixture to create an instance of the TimeSeriesLSTM class with different optimizers
@pytest.fixture(params=optimizers)
def lstm_model(request):
    model = TimeSeriesLSTM(
        ticker="AAPL",
        start_date="2022-01-01",
        end_date="2023-01-01",
        sequence_length=10,
        num_units=64,
        optimizer=request.param,
        log_dir='custom_LSTM_logs'
    )
    return model

# Test case to check if the LSTM model can be created
def test_create_lstm_model(lstm_model):
    assert isinstance(lstm_model, TimeSeriesLSTM)

# Test case to check if the LSTM model can be trained
def test_train_lstm_model(lstm_model):
    lstm_model.train_model(epochs=1, batch_size=32)

# Test case to check if the LSTM model can be evaluated
def test_evaluate_lstm_model(lstm_model):
    test_loss,test_acc = lstm_model.evaluate_model()
    assert test_loss >= 0.0
    assert test_acc >= 0.0

# Test case to check if the LSTM model can make forecasts
def test_forecast_lstm(lstm_model):
    input_data = lstm_model.x_test
    forecasts = lstm_model.forecast(input_data)
    assert len(forecasts) == len(input_data)

# Test case to check if weights can be set and retrieved
def test_set_and_get_weights(lstm_model):
    # Get the initial model weights
    initial_weights = lstm_model.model.get_weights()

    # Create a new instance with the same configuration
    new_lstm_model = TimeSeriesLSTM(
        ticker="AAPL",
        start_date="2022-01-01",
        end_date="2023-01-01",
        sequence_length=10,
        num_units=64,
        optimizer=lstm_model.optimizer,  # Pass the same optimizer
        log_dir='custom_LSTM_logs'
    )

    try:
        new_lstm_model.set_weights(initial_weights)
        new_weights = new_lstm_model.model.get_weights()

        # Check if the shapes of weights match
        assert len(initial_weights) == len(new_weights)
        for i in range(len(initial_weights)):
            assert initial_weights[i].shape == new_weights[i].shape
    except Exception as e:
        pytest.fail(f"Failed to set and retrieve weights: {e}")

if __name__ == '__main__':
    pytest.main()
