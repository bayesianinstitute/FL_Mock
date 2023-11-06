import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import subprocess
from sklearn.model_selection import train_test_split
from sklearn import datasets  
from sklearn.datasets import fetch_california_housing
import datetime
class ANNTabularClassification:
    def __init__(self, optimizer='adam', log="custom_ANN_Classification_log"):
        self.optimizer = optimizer
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()

        # Create a log directory with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.dir_log = f"{log}/fit/{timestamp}"

        self.model = self.build_model()

    def build_model(self):
        # Build a simple ANN model for tabular data
        model = Sequential()
        model.add(Dense(64, activation='relu', input_shape=(self.x_train.shape[1],)))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(3, activation='softmax'))  # Changed output units to match the Iris dataset classes

        model.compile(optimizer=self.optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        return model

    def load_and_preprocess_data(self):
        # Load the Iris dataset
        data = datasets.load_iris()

        # Access the feature data
        X = data.data

        # Access the target labels
        y = data.target

        # Split data into training and testing sets
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        return x_train, y_train, x_test, y_test

    def train_model(self, epochs=10, batch_size=32):
        # Create a TensorBoard callback to log the training process
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=self.dir_log)

        # Train the model and use the TensorBoard callback
        self.model.fit(self.x_train, self.y_train, epochs=epochs, batch_size=batch_size, callbacks=[tensorboard_callback])

    def evaluate_model(self):
        # Evaluate the model on the test data
        test_loss, test_accuracy = self.model.evaluate(self.x_test, self.y_test)
        return test_loss, test_accuracy
    
    def save_model(self, model_filename):
        # Save the model to a file
        self.model.save(model_filename)
        print(f"Model saved to {model_filename}")
    
    def set_weights(self, weights):
        self.model.set_weights(weights)
        return self.model

    def run_tensorboard(self):
        try:
            logdir = f"custom_ANN_Classification_log/fit"  # Specify the log directory
            subprocess.run(["tensorboard", "--logdir", logdir])
        except Exception as e:
            print(f"Error running TensorBoard: {e}")


class ANNTabularLinearRegression:
    def __init__(self, optimizer='adam', log="custom_ANN_Linear_log"):
        self.optimizer = optimizer
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()

        # Create a log directory with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.dir_log = f"{log}/fit/{timestamp}"

        self.model = self.build_model()

    def build_model(self):
        # Build a simple ANN model for regression
        model = Sequential()
        model.add(Dense(64, activation='relu', input_shape=(self.x_train.shape[1],)))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1, activation='linear'))  # Output layer for regression

        model.compile(optimizer=self.optimizer, loss='mean_squared_error', metrics=['mean_absolute_error'])

        return model

    def load_and_preprocess_data(self):
        # Load the California housing dataset
        data = fetch_california_housing()

        # Access the feature data
        X = data.data

        # Access the target values (median house values)
        y = data.target

        # Split data into training and testing sets
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        return x_train, y_train, x_test, y_test

    def train_model(self, epochs=10, batch_size=32):
        # Create a TensorBoard callback to log the training process
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=self.dir_log, histogram_freq=1)  # Set up TensorBoard callback

        # Train the model and use the TensorBoard callback
        self.model.fit(self.x_train, self.y_train, epochs=epochs, batch_size=batch_size, callbacks=[tensorboard_callback])

    def evaluate_model(self):
        # Evaluate the model on the test data
        test_loss, test_mae = self.model.evaluate(self.x_test, self.y_test)
        return test_loss, test_mae

    
    def save_model(self, model_filename):
        # Save the model to a file
        self.model.save(model_filename)
        print(f"Model saved to {model_filename}")
    
    def set_weights(self, weights):
        self.model.set_weights(weights)
        return self.model

    def run_tensorboard(self):
        try:
            logdir = f"custom_ANN_Classification_log/fit"  # Specify the log directory
            subprocess.run(["tensorboard", "--logdir", logdir])
        except Exception as e:
            print(f"Error running TensorBoard: {e}")


            
if __name__ == '__main__':
    tabular_model = ANNTabularClassification('adam')
    tabular_model.train_model(epochs=10, batch_size=32)
    test_loss, test_accuracy = tabular_model.evaluate_model()
    print(f'Test loss: {test_loss:.4f}, Test accuracy: {test_accuracy:.4f}')

    tabular_model.run_tensorboard()


    tabular_regression_model = ANNTabularLinearRegression('adam')
    tabular_regression_model.train_model(epochs=10, batch_size=32)
    test_loss, test_mae = tabular_regression_model.evaluate_model()
    print(f'Test loss: {test_loss:.4f}, Test Mean Absolute Error: {test_mae:.4f}')

    tabular_regression_model.run_tensorboard()