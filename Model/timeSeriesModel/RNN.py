import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import yfinance as yf
from tensorflow.keras.callbacks import TensorBoard

class TimeSeriesRNN:
    def __init__(self, ticker, start_date, end_date, sequence_length, num_units, optimizer='adam', log_dir='custom_RNN_logs'):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.sequence_length = sequence_length
        self.num_units = num_units
        self.optimizer = optimizer
        self.log_dir = log_dir
        self.model = self.build_rnn_model()
        self.data = self.load_and_preprocess_data()

    def build_rnn_model(self):
        model = Sequential()
        model.add(SimpleRNN(self.num_units, input_shape=(self.sequence_length, 1)))
        model.add(Dense(1))  # Single output for time series forecasting

        model.compile(optimizer=self.optimizer, loss='mean_squared_error')
        return model

    def load_and_preprocess_data(self):
        # Fetch historical stock price data from Yahoo Finance
        data = yf.download(self.ticker, start=self.start_date, end=self.end_date)

        # Extract the 'Close' prices as the time series data
        data = data['Close'].values.reshape(-1, 1)

        # Normalize the data to the range [0, 1]
        scaler = MinMaxScaler()
        data = scaler.fit_transform(data)

        return data

    def train_model(self, epochs=100, batch_size=32):
        # Train the RNN model
        x_train, y_train = self.prepare_data(self.data, self.sequence_length)

        # Create a TensorBoard callback to log training metrics
        tensorboard_callback = TensorBoard(log_dir=self.log_dir, histogram_freq=1)

        self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size, callbacks=[tensorboard_callback])

    def prepare_data(self, data, sequence_length):
        # Prepare the data for training
        x, y = [], []
        for i in range(len(data) - sequence_length):
            x.append(data[i:i+sequence_length])
            y.append(data[i+sequence_length])

        x = np.array(x)
        y = np.array(y)

        return x, y

    def calculate_mape(self, y_true, y_pred):
        """
        Calculate Mean Absolute Percentage Error (MAPE).
        Args:
            y_true: Array of true values.
            y_pred: Array of predicted values.
        Returns:
            MAPE score.
        """
        epsilon = 1e-10  # Small value to avoid division by zero
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + epsilon))) * 100
        return mape

    def evaluate_model(self):
        # Evaluate the model on the test data
        x_test, y_test = self.prepare_data(self.data, self.sequence_length)
        y_pred = self.model.predict(x_test)
        mse = mean_squared_error(y_test, y_pred)
        mape = self.calculate_mape(y_test, y_pred)
        return mse, mape

    def forecast(self, input_data):
        # Make predictions using the trained RNN model
        input_data = input_data[-self.sequence_length:]  # Use the most recent data
        input_data = np.reshape(input_data, (1, self.sequence_length, 1))
        forecast = self.model.predict(input_data)
        return forecast
    
    def save_model(self, model_filename):
        # Save the model to a file
        self.model.save(model_filename)
        print(f"Model saved to {model_filename}")
    
    def set_weights(self, weights):
        self.model.set_weights(weights)
        return self.model
        

    def run_tensorboard(self,):
        import subprocess
        try:
            subprocess.run(["tensorboard", "--logdir", self.log_dir])
        except Exception as e:
            print(f"Error running TensorBoard: {e}")

# Usage example:
if __name__ == '__main__':
    # Specify the stock ticker symbol, start and end dates, sequence length, and number of units
    ticker = "AAPL"  # Replace with the desired stock symbol
    start_date = "2022-01-01"
    end_date = "2023-01-01"
    sequence_length = 10
    num_units = 64

    # Create a TimeSeriesRNN object with a custom log directory
    rnn_forecast = TimeSeriesRNN(ticker, start_date, end_date, sequence_length, num_units, optimizer='adam', log_dir='custom_RNN_logs')

    # Train the RNN model
    rnn_forecast.train_model(epochs=100, batch_size=32)

    # Evaluate the model
    mse, mape = rnn_forecast.evaluate_model()
    print(f'Mean Squared Error (MSE): {mse:.4f}')
    print(f'Mean Absolute Percentage Error (MAPE): {mape:.4f}%')

    # Make forecasts
    input_data = rnn_forecast.data  # Use the historical stock price data for forecasting
    forecast = rnn_forecast.forecast(input_data)
    print("Forecast:", forecast)
