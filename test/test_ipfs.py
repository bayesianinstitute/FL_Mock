import os
import shutil
import tempfile
import pytest
from core.IPFS.ipfs import IPFS  # Import your IPFS class from the appropriate location

@pytest.fixture
def ipfs_communicator():
    return IPFS()

@pytest.fixture
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_push_model(ipfs_communicator, temp_dir):
    # Create a temporary model file for testing
    with tempfile.NamedTemporaryFile(delete=False) as temp_model_file:
        temp_model_file.write(b'Test Model Data')

    model_hash = ipfs_communicator.push_model(temp_model_file.name)
    assert model_hash is not None

def test_download_model(ipfs_communicator, temp_dir):
    # Create a temporary model file for testing
    with tempfile.NamedTemporaryFile(delete=False) as temp_model_file:
        temp_model_file.write(b'Test Model Data')

    model_hash = ipfs_communicator.push_model(temp_model_file.name)

    downloaded_model = ipfs_communicator.download_model(model_hash, temp_dir)
    assert downloaded_model is not None

    # Check if the downloaded model file exists
    assert os.path.exists(os.path.join(temp_dir, 'saved_model.keras'))

def test_fetch_model(ipfs_communicator, temp_dir):
    # Create a temporary model file for testing
    with tempfile.NamedTemporaryFile(delete=False) as temp_model_file:
        temp_model_file.write(b'Test Model Data')

    model_hash = ipfs_communicator.push_model(temp_model_file.name)

    model = ipfs_communicator.fetch_model(model_hash)
    assert model is not None
