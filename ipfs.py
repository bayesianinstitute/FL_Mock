import torch
import torch.nn as nn
import torch.optim as optim
import os
import ipfshttpclient
import io

# Define a simple model
class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(10, 1)

    def forward(self, x):
        return self.fc(x)
    
def train_model(worker_id):
    model = SimpleModel()
    optimizer = optim.SGD(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    input_data = torch.randn(100, 10)
    target = torch.randn(100, 1)

    epochs = 100
    for epoch in range(epochs):
        optimizer.zero_grad()
        output = model(input_data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

    # Save the trained model using torch.jit.script
    scripted_model = torch.jit.script(model)
    torch.jit.save(scripted_model, f'trained_model_{worker_id}.pt')
    return 'trained_model.pt'

# IPFS communication class
class IPFS:
    def __init__(self, ipfs_path, device):
        self.ipfs_path = ipfs_path
        self.DEVICE = device
        self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')

    def fetch_model(self, model_hash):
        model_bytes = self.client.cat(model_hash)
        model = torch.jit.load(io.BytesIO(model_bytes), map_location=self.DEVICE)
        return model

    def push_model(self, saved_model_pb_path):
        model_filename = saved_model_pb_path
        model_hash = self.client.add(model_filename)['Hash']
        return model_hash

    def download_model(self, model_hash, destination_folder):
        model_bytes = self.client.cat(model_hash)
        worker_id=3
        # Specify the path for saving the model file locally
        local_model_path = os.path.join(destination_folder, f'model_{worker_id}.pt')

        # Save the downloaded model to the local path
        with open(local_model_path, 'wb') as f:
            f.write(model_bytes)

        # Load the model from the local path
        model = torch.jit.load(local_model_path, map_location=self.DEVICE)
        
        return model

if __name__ == "__main__":
    ipfs_path = '/your/ipfs/path'
    device = 'cpu'

    ipfs_communicator = IPFS(ipfs_path, device)

    # Train the model and get the model file path
    trained_model_path = train_model()

    # Push the trained model to IPFS and get the hash
    model_hash = ipfs_communicator.push_model(trained_model_path)

    # Access the model hash
    print("Model Hash:", model_hash)

    # Define the destination folder to save the downloaded model
    destination_folder = 'downloaded_models'

    # Download the model and save it to the destination folder
    downloaded_model = ipfs_communicator.download_model(model_hash, destination_folder)

    # # You can now use the downloaded model for inference
    # input_data = torch.randn(1, 10)  # Replace with your input data
    # output = downloaded_model(input_data)
    # print("Inference result:", output)
