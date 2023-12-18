import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import SimpleRNN, Dense
import yfinance as yf
import mlflow
import mlflow.keras
import warnings
from datetime import datetime

class TimeSeriesRNN:
    def __init__(self, ticker="AAPL", start_date="2022-01-01", end_date="2023-01-01", sequence_length=10, num_units=64, optimizer='adam', log_dir='custom_RNN_logs'):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.sequence_length = sequence_length
        self.num_units = num_units
        self.optimizer = optimizer
        self.log_dir = log_dir
        self.model = self.build_model()
        self.data = self.load_and_preprocess_data()

    def build_model(self):
        model = Sequential()
        model.add(SimpleRNN(self.num_units, input_shape=(self.sequence_length, 1)))
        model.add(Dense(1))

        model.compile(optimizer=self.optimizer, loss='mean_squared_error')
        return model

    def load_and_preprocess_data(self):
        try:
            data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
            data = data['Close'].values.reshape(-1, 1)
            scaler = MinMaxScaler()
            data = scaler.fit_transform(data)
            return data
        except Exception as e:
            print(f"Error load_and_preprocess_data: {e}")


    def train_model(self,rounds=None, epochs=10, batch_size=32 ):
        try:

            mlflow.start_run(run_name=f'{self.name}_Rounds:{rounds}')

            # Train the model and log metrics using MLflow
            mlflow.tensorflow.autolog()
            history = self.model.fit(
                self.x_train, self.y_train,
                epochs=epochs, batch_size=batch_size,
                validation_data=(self.x_test, self.y_test)
            )

            # Extract final values
            final_loss = history.history['loss'][-1]
            final_accuracy = history.history['accuracy'][-1]
            final_val_loss = history.history['val_loss'][-1]
            final_val_accuracy = history.history['val_accuracy'][-1]


            return final_loss, final_accuracy, final_val_loss, final_val_accuracy

        except Exception as e:
            print(f"Error training the model: {e}")

    def prepare_data(self, data, sequence_length):
        x, y = [], []
        for i in range(len(data) - sequence_length):
            x.append(data[i:i+sequence_length])
            y.append(data[i+sequence_length])

        x = np.array(x)
        y = np.array(y)

        return x, y



    def save_model(self, model_filename):
        try:
            # Save the model to a file and log as an artifact
            model_path = f"mlruns/models/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}/{model_filename}"
            
            # Suppress Setuptools warning
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                self.model.save(model_path, save_format='tf')
                self.model.save(model_filename)
                print(f"Model saved to {model_filename}")

            # Save model summary to a text file
            summary_path = f"mlruns/models/{model_filename}_summary.txt"
            with open(summary_path, "w") as f:
                self.model.summary(print_fn=lambda x: f.write(x + '\n'))

            mlflow.log_artifact(model_path)
            mlflow.log_artifact(summary_path)
            mlflow.end_run()

            print(f"Model and summary saved as artifacts: {model_filename}")
        except Exception as e:
            print(f"Error saving the model: {e}")

    def set_weights(self, weights):
        self.model.set_weights(weights)
        return self.model



# Usage example:
if __name__ == '__main__':
    ticker = "AAPL"
    start_date = "2022-01-01"
    end_date = "2023-01-01"
    sequence_length = 10
    num_units = 64

    rnn_forecast = TimeSeriesRNN(ticker, start_date, end_date, sequence_length, num_units, optimizer='adam', log_dir='custom_RNN_logs')
    final_loss, final_accuracy, final_val_loss, final_val_accuracy =rnn_forecast = TimeSeriesRNN(ticker, start_date, end_date, sequence_length, num_units, optimizer='adam', log_dir='custom_RNN_logs')
    rnn_forecast.train_model(epochs=100, batch_size=32)
    print(f'Final Training Loss: {final_loss:.4f}')
    print(f'Final Training Accuracy: {final_accuracy:.4f}')
    print(f'Final Validation Loss: {final_val_loss:.4f}')
    print(f'Final Validation Accuracy: {final_val_accuracy:.4f}')
    rnn_forecast.save_model("rnn_model.h5")
    print("Completed training")
