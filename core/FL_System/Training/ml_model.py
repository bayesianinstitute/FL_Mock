import tensorflow as tf
from tensorflow import keras

class MachineLearningModelTrainer:
    def __init__(self, dataset_name, model_name):
        self.dataset_name = dataset_name
        self.model_name = model_name
        self.model = None

    def load_dataset(self):
        if self.dataset_name == "mnist":
            (train_images, train_labels), (test_images, test_labels) = keras.datasets.mnist.load_data()
        elif self.dataset_name == "cifar10":
            (train_images, train_labels), (test_images, test_labels) = keras.datasets.cifar10.load_data()
        else:
            raise ValueError("Unsupported dataset")

        return train_images, train_labels, test_images, test_labels

    def preprocess_data(self, train_images, test_images):
        train_images = train_images / 255.0
        test_images = test_images / 255.0
        return train_images, test_images

    def build_model(self):
        if self.model_name == "simple_nn":
            self.model = keras.Sequential([
                keras.layers.Flatten(input_shape=(28, 28)),
                keras.layers.Dense(128, activation='relu'),
                keras.layers.Dense(10, activation='softmax')
            ])
        elif self.model_name == "cnn":
            self.model = keras.Sequential([
                keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
                keras.layers.MaxPooling2D((2, 2)),
                keras.layers.Flatten(),
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dense(10, activation='softmax')
            ])
        else:
            raise ValueError("Unsupported model")

    def train_model(self, train_images, train_labels, epochs=5):
        self.model.compile(optimizer='adam',
                          loss='sparse_categorical_crossentropy',
                          metrics=['accuracy'])
        self.model.fit(train_images, train_labels, epochs=epochs)

    def evaluate_model(self, test_images, test_labels):
        test_loss, test_accuracy = self.model.evaluate(test_images, test_labels)
        return test_accuracy

    def save_model(self, filename):
        self.model.save(filename)

    def train_machine_learning_model(self):
        train_images, train_labels, test_images, test_labels = self.load_dataset()
        train_images, test_images = self.preprocess_data(train_images, test_images)
        self.build_model()
        self.train_model(train_images, train_labels)
        test_accuracy = self.evaluate_model(test_images, test_labels)
        # Optional: Save the trained model
        # self.save_model("trained_model.keras")
        return f"Machine learning model trained with test accuracy: {test_accuracy:.2f}."

if __name__ == "__main__":
    # Example: Train a simple neural network on the MNIST dataset
    trainer = MachineLearningModelTrainer(dataset_name="mnist", model_name="simple_nn")
    result = trainer.train_machine_learning_model()
    print(result)

    # Example: Train a CNN on the CIFAR-10 dataset
    trainer = MachineLearningModelTrainer(dataset_name="cifar10", model_name="cnn")
    result = trainer.train_machine_learning_model()
    print(result)
