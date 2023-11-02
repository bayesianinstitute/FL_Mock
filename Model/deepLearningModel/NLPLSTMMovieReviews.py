from keras.datasets import imdb
from keras.layers import Embedding, LSTM, Dense
from keras.preprocessing import sequence
from keras.callbacks import TensorBoard
from keras.models import Sequential

import subprocess

class NLPLSTMMovieReviews:
    def __init__(self, optimizer='adam', log_dir='custom_NLPLSTMMovieReviews_logs'):
        self.optimizer = optimizer
        self.model = self.build_model()
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()
        self.log_dir = log_dir
        self.tensorboard_callback = TensorBoard(log_dir=self.log_dir, histogram_freq=1)

    def build_model(self):
        # Build an LSTM model for text classification
        model = Sequential()
        model.add(Embedding(input_dim=5000, output_dim=64))  # You can adjust input_dim and output_dim as needed
        model.add(LSTM(100))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(optimizer=self.optimizer, loss='binary_crossentropy', metrics=['accuracy'])

        return model

    def load_and_preprocess_data(self):
        # Load IMDB dataset
        (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=5000)  # You can adjust the number of words

        # Pad sequences to a fixed length (e.g., 200)
        max_review_length = 200
        x_train = sequence.pad_sequences(x_train, maxlen=max_review_length)
        x_test = sequence.pad_sequences(x_test, maxlen=max_review_length)

        return x_train, y_train, x_test, y_test

    def train_model(self, epochs=5, batch_size=32):
        # Train the model with TensorBoard callback
        self.model.fit(
            self.x_train, self.y_train,
            epochs=epochs, batch_size=batch_size,
            validation_data=(self.x_test, self.y_test),
            callbacks=[self.tensorboard_callback]
        )

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
            subprocess.run(["tensorboard", "--logdir", self.log_dir])
        except Exception as e:
            print(f"Error running TensorBoard: {e}")

if __name__ == '__main__':
    imdb_model = NLPLSTMMovieReviews('adam')
    imdb_model.train_model(epochs=5, batch_size=32)
    test_loss, test_accuracy = imdb_model.evaluate_model()
    print(f'Test loss: {test_loss:.4f}, Test accuracy: {test_accuracy:.4f}')

    # Run TensorBoard in the background
    imdb_model.run_tensorboard()
