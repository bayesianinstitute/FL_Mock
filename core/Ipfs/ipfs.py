import os
import ipfshttpclient
import io
import tensorflow as tf
from tensorflow import keras
import tempfile


# IPFS communication class (for to the Tensorflow version)
class IPFS:
    def __init__(self,):
        self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')

    def fetch_model(self, model_hash):
        model_bytes = self.client.cat(model_hash)
                # Create a temporary file to save the model bytes
        with tempfile.NamedTemporaryFile(delete=False) as temp_model_file:
            temp_model_file.write(model_bytes)

        # Load the model from the temporary file
        model = keras.models.load_model(temp_model_file.name)

        return model


    def push_model(self, saved_model_path):
        
        model_hash = self.client.add(saved_model_path)['Hash']
        return model_hash

    def download_model(self, model_hash, destination_folder):
        # Create the directory if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)

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