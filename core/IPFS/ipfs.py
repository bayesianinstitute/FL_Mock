import os
import ipfshttpclient
import io
import tensorflow as tf
from tensorflow import keras
import tempfile
from core.Logs_System.logger import Logger

# IPFS communication class (for to the Tensorflow version)
class IPFS:
    def __init__(self,connection_link='/ip4/127.0.0.1/tcp/5001/http'):
        self.logger=Logger(name='ipfs_logger').get_logger()
        self.client = self._connect_to_ipfs(connection_link)
    
    def _connect_to_ipfs(self,connect_link):
        try:
            ipfs_conn_obj=ipfshttpclient.connect(connect_link)
            self.logger.info("Connected to IPFS")
            return ipfs_conn_obj
        except Exception as e:
            self.logger.error(f"Error during IPFS connection: {e}")
            self.logger.critical("unable to connect to IPFS")
            import sys
            sys.exit(1)

    def fetch_model(self, model_hash):
        self.logger.debug(f"Model hash: {model_hash}")
        try:
            # Retrieve the model bytes from the client using model_hash
            model_bytes = self.client.cat(model_hash)
        except Exception as e:
            self.logger.error(f"Error retrieving model with hash {model_hash}: {str(e)}")
            return None

        # Create a temporary file to save the model bytes
        with tempfile.NamedTemporaryFile(delete=False) as temp_model_file:
            try:
                # Write the model bytes to the temporary file
                temp_model_file.write(model_bytes)
            except Exception as e:
                # Handle the case when there's an issue writing to the temporary file
                self.logger.error(f"Error writing model bytes to temporary file: {str(e)}")
                return None
        try:
            model = keras.models.load_model(temp_model_file.name)
        except Exception as e:
            self.logger.error(f"Error loading model from temporary file: {str(e)}")
            return None
        finally:
            temp_model_file.close()
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
