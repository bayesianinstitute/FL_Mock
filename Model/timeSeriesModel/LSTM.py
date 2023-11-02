import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard



class TimeSeriesLSTM:
    def __init__(self, ticker="AAPL",
                 start_date="2022-01-01",
                 end_date= "2023-01-01",
                 sequence_length=10, 
                 num_units=64, 
                 optimizer='adam',
                 log_dir='custom_LSTM_logs'):
        
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.sequence_length = sequence_length
        self.num_units = num_units
        self.optimizer = optimizer
        self.model = self.build_lstm_model()
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()
        self.log_dir=log_dir

    def build_lstm_model(self):
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.LSTM(self.num_units, input_shape=(self.sequence_length, 1)))
        model.add(tf.keras.layers.Dense(1))  # Single output for time series forecasting
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

        # Split the data into training and test sets
        train_size = int(len(data) * 0.8)
        train_data, test_data = data[0:train_size], data[train_size:]

        x_train, y_train, x_test, y_test = [], [], [], []

        for i in range(self.sequence_length, len(train_data)):
            x_train.append(train_data[i - self.sequence_length:i, 0])
            y_train.append(train_data[i, 0])

        for i in range(self.sequence_length, len(test_data)):
            x_test.append(test_data[i - self.sequence_length:i, 0])
            y_test.append(test_data[i, 0])

        x_train, y_train, x_test, y_test = np.array(x_train), np.array(y_train), np.array(x_test), np.array(y_test)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

        return x_train, y_train, x_test, y_test

    def train_lstm_model(self, epochs=100, batch_size=32):
        # Train the LSTM model
        tensorboard_callback = TensorBoard(log_dir=self.log_dir, histogram_freq=1)

        self.model.fit(self.x_train, self.y_train, epochs=epochs, batch_size=batch_size,callbacks=[tensorboard_callback])

    def evaluate_lstm_model(self):
        # Evaluate the LSTM model on the test data
        test_loss = self.model.evaluate(self.x_test, self.y_test)
        return test_loss

    def forecast_lstm(self, input_data):
        # Make predictions using the trained LSTM model
        predictions = self.model.predict(input_data)
        return predictions
    
    def save_model(self, model_filename):
        # Save the model to a file
        self.model.save(model_filename)
        print(f"Model saved to {model_filename}")
    
    def set_weights(self, weights):
        self.model.set_weights(weights)
        return self.model
        

    def run_tensorboard(self):
        import subprocess
        try:
            log_dir = f"custom_LSTM_logs/fit"  # Specify the log directory
            tensorboard_callback = TensorBoard(log_dir=log_dir, write_graph=True)
            subprocess.Popen(["cmd.exe", "/k", "tensorboard", "--logdir", log_dir])
        except Exception as e:
            print(f"Error running TensorBoard: {e}")

# Usage example:
if __name__ == '__main__':
    # Specify the stock ticker symbol, start and end dates, sequence length, and number of LSTM units
    ticker = "AAPL"  # Replace with the desired stock symbol
    start_date = "2022-01-01"
    end_date = "2023-01-01"
    sequence_length = 10
    num_units = 64

    # Create a TimeSeriesLSTM object
    lstm_forecast = TimeSeriesLSTM(ticker, start_date, end_date, sequence_length, num_units, optimizer='adam',log_dir='custom_LSTM_logs')

    # Train the LSTM model
    lstm_forecast.train_lstm_model(epochs=100, batch_size=32)

    # Evaluate the model
    test_loss = lstm_forecast.evaluate_lstm_model()
    print(f'Test Loss: {test_loss:.4f}')

    # Make forecasts
    input_data = lstm_forecast.x_test  # Use the test data for forecasting
    forecasts = lstm_forecast.forecast_lstm(input_data)
    print("Forecasts:", forecasts)
