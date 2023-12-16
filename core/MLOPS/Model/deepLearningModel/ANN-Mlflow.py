
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn import datasets
from sklearn.datasets import fetch_california_housing
import datetime
import mlflow
import mlflow.tensorflow

class ANNTabularClassification:
    def __init__(self, optimizer='adam'):
        self.optimizer = optimizer
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()

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
        # Start a new MLflow run
        with mlflow.start_run():
            # Train the model
            self.model.fit(self.x_train, self.y_train, epochs=epochs, batch_size=batch_size)

            # Log metrics
            mlflow.log_params({'epochs': epochs, 'batch_size': batch_size})
            test_loss, test_accuracy = self.model.evaluate(self.x_test, self.y_test)
            mlflow.log_metrics({'test_loss': test_loss, 'test_accuracy': test_accuracy})

    def save_model(self, model_filename):
        # Save the model to a file
        self.model.save(model_filename)
        print(f"Model saved to {model_filename}")

    def set_weights(self, weights):
        self.model.set_weights(weights)
        return self.model


class ANNTabularLinearRegression:
    def __init__(self, optimizer='adam'):
        self.optimizer = optimizer
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()

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
        # Start a new MLflow run
        with mlflow.start_run():
            # Train the model
            self.model.fit(self.x_train, self.y_train, epochs=epochs, batch_size=batch_size)

            # Log metrics
            mlflow.log_params({'epochs': epochs, 'batch_size': batch_size})
            test_loss, test_mae = self.model.evaluate(self.x_test, self.y_test)
            mlflow.log_metrics({'test_loss': test_loss, 'test_mae': test_mae})

    def save_model(self, model_filename):
        # Save the model to a file
        self.model.save(model_filename)
        print(f"Model saved to {model_filename}")

if __name__ == '__main__':
    # Initialize MLflow
    mlflow.tensorflow.autolog()

    tabular_model = ANNTabularClassification('adam')
    tabular_model.train_model(epochs=10, batch_size=32)

    tabular_regression_model = ANNTabularLinearRegression('adam')
    tabular_regression_model.train_model(epochs=10, batch_size=32)
