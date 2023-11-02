from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.datasets import mnist
from tensorflow.keras.callbacks import TensorBoard
import subprocess

class CNNMnist:
    def __init__(self, optimizer='adam',log_dir='custom_CNNMnist_logs'):
        self.optimizer = optimizer
        self.model = self.build_model()
        self.x_train, self.y_train, self.x_test, self.y_test = self.load_and_preprocess_data()
        self.log_dir=log_dir
        self.tensorboard_callback = TensorBoard(log_dir=self.log_dir, histogram_freq=1)

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

    def load_and_preprocess_data(self,subset_size=1000):
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

    def train_model(self, epochs=10, batch_size=32,):
        # Train the model with TensorBoard callback
        self.model.fit(
            self.x_train, self.y_train,
            epochs=epochs, batch_size=batch_size,
            validation_data=(self.x_test, self.y_test),
            callbacks=[self.tensorboard_callback]
        )

    def evaluate_model(self,):
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
        

    def run_tensorboard(self,):
        try:
            subprocess.run(["tensorboard", "--logdir", self.log_dir])
        except Exception as e:
            print(f"Error running TensorBoard: {e}")

if __name__ == '__main__':
    mnist_model = CNNMnist('adam')
    mnist_model.train_model(epochs=5, batch_size=32)
    test_loss, test_accuracy = mnist_model.evaluate_model()
    print(f'Test loss: {test_loss:.4f}, Test accuracy: {test_accuracy:.4f}')

    # Run TensorBoard in the background
    mnist_model.run_tensorboard()  # Use the same log directory specified in the TensorBoard callback
