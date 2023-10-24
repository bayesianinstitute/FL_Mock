import os
import ipfshttpclient
import io
import tensorflow as tf
from tensorflow import keras

# Define a simple model using Keras
model = keras.Sequential([
    keras.layers.Dense(1, input_shape=(10,))
])

model.compile(optimizer='sgd', loss='mean_squared_error')

# Generate some random data for training
input_data = tf.random.normal((100, 10))
target = tf.random.normal((100, 1))

# Train the model
model.fit(input_data, target, epochs=100)

# Save the trained model using Keras's format
model.save('saved_model.h5')

# IPFS communication class (similar to the PyTorch version)
class IPFS:
    def __init__(self,):
        self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')

    def fetch_model(self, model_hash):
        model_bytes = self.client.cat(model_hash)
        model = keras.models.load_model(io.BytesIO(model_bytes))
        return model

    def push_model(self, saved_model_path):
        model_hash = self.client.add(saved_model_path)['Hash']
        return model_hash

    def download_model(self, model_hash, destination_folder):
        model_bytes = self.client.cat(model_hash)

        # Specify the path for saving the model file locally
        local_model_path = os.path.join(destination_folder, 'model.h5')

        with open(local_model_path, 'wb') as f:
            f.write(model_bytes)

        # Load the model from the local path
        model = keras.models.load_model(local_model_path)
        return model

# testing IPFS Class
if __name__ == "__main__":
    

    ipfs_communicator = IPFS()


    # Define the destination folder to save the downloaded model
    destination_folder = 'downloaded_models'

    # Ensure the 'downloaded_models' directory exists
    os.makedirs(destination_folder)


    # Push the trained model to IPFS and get the hash
    model_hash = ipfs_communicator.push_model('saved_model.h5')

    # Access the model hash
    print("Model Hash:", model_hash)

    # Download the model and save it to the destination folder
    downloaded_model = ipfs_communicator.download_model(model_hash, destination_folder)
    print("Model downloaded:", downloaded_model)


    # model=ipfs_communicator.fetch_model(model_hash)

    # model.summary()