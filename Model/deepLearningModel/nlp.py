from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.datasets import imdb

# Load IMDb dataset
def load_dataset():
    (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=10000)

    # Preprocess data and pad sequences
    x_train = keras.preprocessing.sequence.pad_sequences(x_train, maxlen=100)
    x_test = keras.preprocessing.sequence.pad_sequences(x_test, maxlen=100)

    return x_train, x_test,y_train,y_test

def get_model_nlp():
    # Build and compile a simple LSTM model
    model = Sequential()
    model.add(Embedding(input_dim=10000, output_dim=128))
    model.add(LSTM(128))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    return model

# def train()
#     # Train the model
#     model.fit(x_train, y_train, epochs=5, batch_size=32, validation_data=(x_test, y_test))
