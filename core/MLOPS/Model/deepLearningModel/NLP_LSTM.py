from keras.datasets import imdb
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing import sequence
from keras.models import Sequential
from datetime import datetime
import mlflow
import mlflow.keras

class NLPLSTM:
    def __init__(self, ip="http://localhost",port=5000,optimizer='adam', experiment_name='custom_NLPLSTMMovieReviews_experiment'):
        self.optimizer = optimizer
        self.model = self.build_model()
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()

        # Start MLflow experiment
        self.name = "NLP_LSTM_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.url=f'{ip}:{port}'
        self.url = 'http://localhost:5000'  # Update with your MLflow server URL
        self.config_mlflow(experiment_name, self.url)

    def config_mlflow(self, experiment_name, url):
        try:
            mlflow.set_tracking_uri(url)
            mlflow.set_experiment(experiment_name)
        except Exception as e:
            print(f"Error configuring MLflow: {e}")

    def build_model(self):
        # Build an LSTM model for text classification
        model = Sequential()
        model.add(Embedding(input_dim=5000, output_dim=64))
        model.add(LSTM(100))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(optimizer=self.optimizer, loss='binary_crossentropy', metrics=['accuracy'])

        return model

    def load_and_preprocess_data(self):
        # Load IMDB dataset
        (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=1000)

        # Pad sequences to a fixed length (e.g., 200)
        max_review_length = 200
        x_train = sequence.pad_sequences(x_train, maxlen=max_review_length)
        x_test = sequence.pad_sequences(x_test, maxlen=max_review_length)

        return x_train, y_train, x_test, y_test

    def train_model(self, epochs=5, batch_size=32):
        try:
            mlflow.start_run(run_name=f'{self.name}')

            # Train the model and log metrics using MLflow
            mlflow.keras.autolog()
            history=self.model.fit(
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
    imdb_model = NLPLSTM('adam')
    final_loss, final_accuracy, final_val_loss, final_val_accuracy =imdb_model.train_model(epochs=5, batch_size=32)

    print(f'Final Training Loss: {final_loss:.4f}')
    print(f'Final Training Accuracy: {final_accuracy:.4f}')
    print(f'Final Validation Loss: {final_val_loss:.4f}')
    print(f'Final Validation Accuracy: {final_val_accuracy:.4f}')
    imdb_model.save_model("imdb_model.h5")
    print("Completed training")
