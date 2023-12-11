from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.datasets import mnist
import os
from datetime import datetime
import mlflow
import mlflow.keras
import mlflow.tensorflow
import warnings

class CNNMnist:
    def __init__(self, optimizer='adam', experiment_name='custom_CNNMnist_experiment'):
        self.optimizer = optimizer
        self.model = self.build_model()
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()

        # Start MLflow experiment
        self.name = "CNN_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.config_mlflow(experiment_name)

    def config_mlflow(self,experiment_name):
        try:
            mlflow.set_tracking_uri("http://localhost:5000")  
            mlflow.set_experiment(experiment_name)
            mlflow.start_run(run_name=self.name)
        except Exception as e:
            print(f"Error configuring MLflow: {e}")

    def build_model(self):
        # Build a simple CNN model
        model = Sequential()
        model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(28, 28, 1)))
        model.add(MaxPooling2D((2, 2)))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D((2, 2)))
        model.add(Flatten())
        model.add(Dense(64, activation='relu'))
        model.add(Dense(10, activation='softmax'))

        model.compile(optimizer=self.optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model

    def load_and_preprocess_data(self, subset_size=1000):
        # Load MNIST dataset
        (x_train, y_train), (x_test, y_test) = mnist.load_data()

        # Select a smaller subset of the data
        x_train = x_train[:subset_size]
        y_train = y_train[:subset_size]
        x_test = x_test[:subset_size]
        y_test = y_test[:subset_size]

        # Preprocess data
        x_train = x_train.astype('float32') / 255.0
        x_test = x_test.astype('float32') / 255.0
        x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
        x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)

        return x_train, y_train, x_test, y_test

    def train_model(self, epochs=10, batch_size=32):
        try:
            # Train the model and log metrics using MLflow
            self.model.fit(
                self.x_train, self.y_train,
                epochs=epochs, batch_size=batch_size,
                validation_data=(self.x_test, self.y_test)
            )
        except Exception as e:
            print(f"Error training the model: {e}")

    def evaluate_model(self):
        # Evaluate the model on the test data
        test_loss, test_accuracy = self.model.evaluate(self.x_test, self.y_test)
        mlflow.log_metric("test_loss", test_loss)
        mlflow.log_metric("test_accuracy", test_accuracy)
        return test_loss, test_accuracy

    def save_model(self, model_filename):
        try:
            # Save the model to a file and log as an artifact
            model_path = f"mlruns/models/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}/{model_filename}"  # Specify a subdirectory for models
            mlflow.keras.save_model(self.model, model_path)
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

  

if __name__ == '__main__':
    mnist_model = CNNMnist('adam')
    mnist_model.train_model(epochs=5, batch_size=32)
    test_loss, test_accuracy = mnist_model.evaluate_model()
    print(f'Test loss: {test_loss:.4f}, Test accuracy: {test_accuracy:.4f}')
    mnist_model.save_model("saved_model.h5")
    print("Completed training")
