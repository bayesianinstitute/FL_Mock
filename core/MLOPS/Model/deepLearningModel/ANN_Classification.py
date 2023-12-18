from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn import datasets
import datetime
import mlflow
import mlflow.keras
import mlflow.tensorflow

class ANNTabularClassification:
    def __init__(self,ip="http://localhost",port=5000, optimizer='adam', experiment_name='custom_ANN_Classification_experiment'):
        self.optimizer = optimizer
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()

        # Start MLflow experiment
        self.name = "ANN_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.url=f'{ip}:{port}'

        self.config_mlflow(experiment_name, self.url)

        self.model = self.build_model()

    def config_mlflow(self, experiment_name, url):
        try:
            mlflow.set_tracking_uri(url)
            mlflow.set_experiment(experiment_name)
        except Exception as e:
            print(f"Error configuring MLflow: {e}")

    def build_model(self):
        # Build a simple ANN model for tabular data
        model = Sequential()
        model.add(Dense(64, activation='relu', input_shape=(self.x_train.shape[1],)))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(3, activation='softmax'))

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
            model_path = f"mlruns/models/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}/{model_filename}"
            self.model.save(model_path)
            mlflow.log_artifact(model_path)
            mlflow.end_run()

            print(f"Model saved as artifact: {model_filename}")
        except Exception as e:
            print(f"Error saving the model: {e}")

    def set_weights(self, weights):
        self.model.set_weights(weights)
        return self.model


if __name__ == '__main__':
    # Example usage:
    ann_model = ANNTabularClassification()
    final_loss, final_accuracy, final_val_loss, final_val_accuracy=ann_model.train_model(rounds=1,epochs=5, batch_size=32)

    print(f'Final Training Loss: {final_loss:.4f}')
    print(f'Final Training Accuracy: {final_accuracy:.4f}')
    print(f'Final Validation Loss: {final_val_loss:.4f}')
    print(f'Final Validation Accuracy: {final_val_accuracy:.4f}')

    ann_model.save_model("ann_model.h5")
    print("Completed training")



