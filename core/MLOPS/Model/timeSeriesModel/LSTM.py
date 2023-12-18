import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from keras.layers import LSTM, Dense
from keras.models import Sequential
import mlflow
import mlflow.keras
import warnings

class TimeSeriesLSTM:
    def __init__(self,ip="http://localhost",port=5000, ticker="AAPL", start_date="2022-01-01", end_date="2023-01-01", sequence_length=10, num_units=64, optimizer='adam', experiment_name='custom_LSTM_logs'):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.sequence_length = sequence_length
        self.num_units = num_units
        self.optimizer = optimizer
        self.model = self.build_model()
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()
        self.name = "LSTM_Time" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.url=f'{ip}:{port}'

        self.config_mlflow(experiment_name,self.url)

    def config_mlflow(self,experiment_name,url):
        try:
            mlflow.set_tracking_uri(url)  
            mlflow.set_experiment(experiment_name)
        except Exception as e:
            print(f"Error configuring MLflow: {e}")

    def build_model(self):
        model = Sequential()
        model.add(LSTM(self.num_units, input_shape=(self.sequence_length, 1)))
        model.add(Dense(1))

        model.compile(optimizer=self.optimizer, loss='mean_squared_error', metrics=['accuracy'])

        return model

    def load_and_preprocess_data(self):
        try:
            data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
            data = data['Close'].values.reshape(-1, 1)
            scaler = MinMaxScaler()
            data = scaler.fit_transform(data)

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

    lstm_forecast = TimeSeriesLSTM(ticker, start_date, end_date, sequence_length, num_units, optimizer='adam', experiment_name='custom_LSTM_logs')
    final_loss, final_accuracy, final_val_loss, final_val_accuracy =lstm_forecast.train_model(epochs=100, batch_size=32)
    print(f'Final Training Loss: {final_loss:.4f}')
    print(f'Final Training Accuracy: {final_accuracy:.4f}')
    print(f'Final Validation Loss: {final_val_loss:.4f}')
    print(f'Final Validation Accuracy: {final_val_accuracy:.4f}')
    lstm_forecast.save_model("lstm_model.h5")
    print("Completed training")
