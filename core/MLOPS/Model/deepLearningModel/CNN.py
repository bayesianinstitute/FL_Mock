from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from keras.datasets import mnist
from datetime import datetime
import mlflow
import mlflow.keras
import mlflow.tensorflow
import warnings
import os


class CNNMnist:
    def __init__(self, optimizer='adam', experiment_name='custom_CNNMnist_experiment'):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        warnings.filterwarnings("ignore", category=UserWarning, message=".*Setuptools is replacing distutils.*")
     

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
    
    def set_weights(self, weights):
        self.model.set_weights(weights)
        return self.model

    def save_model(self, model_filename):
        try:
            # Save the model to a file and log as an artifact
            model_path = f"mlruns/models/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}/{model_filename}"
            
            # Suppress Setuptools warning
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                self.model.save(model_path, save_format='tf')

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
        # Suppress TensorFlow informational messages

    mnist_model = CNNMnist('adam')
    final_loss, final_accuracy, final_val_loss, final_val_accuracy = mnist_model.train_model(epochs=5, batch_size=32)

    print(f'Final Training Loss: {final_loss:.4f}')
    print(f'Final Training Accuracy: {final_accuracy:.4f}')
    print(f'Final Validation Loss: {final_val_loss:.4f}')
    print(f'Final Validation Accuracy: {final_val_accuracy:.4f}')
    mnist_model.save_model("saved_model.h5")
    print("Completed training")
