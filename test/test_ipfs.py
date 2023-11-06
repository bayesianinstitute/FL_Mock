import os
import tempfile
import pytest
from tensorflow import keras
from core.IPFS.ipfs import IPFS

# Sample model for testing
def create_sample_model():
    model = keras.Sequential([
        keras.layers.Dense(64, activation='relu', input_shape=(10,)),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(1, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

@pytest.fixture(scope="module")
def test_model():
    return create_sample_model()

@pytest.fixture(scope="module")
def test_saved_model_path(test_model):
    # Create a temporary directory and save the model to it
    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = os.path.join(temp_dir, 'model.h5')
        test_model.save(model_path)
        yield model_path

@pytest.fixture(scope="module")
def test_ipfs():
    return IPFS()

def test_fetch_model(test_ipfs, test_model, test_saved_model_path):
    model_hash = test_ipfs.push_model(test_saved_model_path)
    fetched_model = test_ipfs.fetch_model(model_hash)
    
    # Compare the fetched model with the original model
    assert isinstance(fetched_model, keras.models.Sequential)
    assert test_model.input_shape == fetched_model.input_shape
    assert test_model.output_shape == fetched_model.output_shape

def test_push_model(test_ipfs, test_saved_model_path):
    model_hash = test_ipfs.push_model(test_saved_model_path)
    assert isinstance(model_hash, str)

def test_download_model(test_ipfs, test_model, test_saved_model_path):
    model_hash = test_ipfs.push_model(test_saved_model_path)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        fetched_model = test_ipfs.download_model(model_hash, temp_dir)
        
        # Compare the fetched model with the original model
        assert isinstance(fetched_model, keras.models.Sequential)
        assert test_model.input_shape == fetched_model.input_shape
        assert test_model.output_shape == fetched_model.output_shape
