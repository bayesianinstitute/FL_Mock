import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import TensorBoard
import json

# Load the dataset from the JSON file
with open("data.json", "r") as json_file:
    dataset = json.load(json_file)

x_train, y_train, x_test, y_test = dataset["x_train"], dataset["y_train"], dataset["x_test"], dataset["y_test"]

# Create a linear regression model
model = Sequential([
    Dense(1, input_shape=(len(x_train[0]),))  # Input shape should match the number of features
])

# Compile the model
model.compile(optimizer='sgd', loss='mean_squared_error')

# Define a TensorBoard callback
tensorboard_callback = TensorBoard(log_dir="./log")

# Train the model with the TensorBoard callback
model.fit(x_train, y_train, epochs=20, batch_size=32, validation_data=(x_test, y_test), callbacks=[tensorboard_callback])

# You can run TensorBoard in your terminal to visualize the logs:
# tensorboard --logdir=./logs

# Evaluate the model on test data
loss = model.evaluate(x_test, y_test)
print(f"Test loss: {loss}")
