import tensorflow as tf
from tensorflow import keras
from keras import layers
import numpy as np

# Load the MNIST dataset
mnist = keras.datasets.mnist
(train_images, train_labels), (test_images, test_labels) = mnist.load_data()

# Preprocess the data
train_images = train_images / 255.0
test_images = test_images / 255.0

# Build a simple neural network model
model = keras.Sequential([
    layers.Flatten(input_shape=(28, 28)),  # Flatten the 28x28 images to 1D array
    layers.Dense(128, activation='relu'),
    layers.Dense(10, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
model.fit(train_images, train_labels, epochs=5)



# Save the model
model.save('mnist_model.keras')

# Load the model from the file
loaded_model = keras.models.load_model('mnist_model.keras')

# Make predictions with the loaded model
predictions = loaded_model.predict(test_images)

# Print the first prediction
print("First prediction:", predictions[0])

prev_weights = model.get_weights()
new_weights = loaded_model.get_weights()

# Check if the weights are approximately the same within the tolerance for each layer
for layer_prev, layer_new in zip(prev_weights, new_weights):
    if np.allclose(layer_prev, layer_new, rtol=1e-5, atol=1e-5):
        print("The weights for this layer are approximately the same within the tolerance.")
    else:
        print("The weights for this layer are not exactly the same.")
