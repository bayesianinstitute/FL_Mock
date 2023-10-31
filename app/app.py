import tensorflow as tf
from tensorflow import keras
from flask import Flask, request, jsonify, render_template
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import plotly.express as px
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from sklearn.utils.multiclass import unique_labels
app = Flask(__name__)

# Create a simple UI for model selection and training
@app.route('/webpage')
def webpage():
    return render_template('webpage.html')

# Load and preprocess the MNIST dataset
def load_and_preprocess_dataset(dataset_name):
    if dataset_name == 'MNIST':
        dataset = keras.datasets.mnist
    elif dataset_name == 'FashionMNIST':
        dataset = keras.datasets.fashion_mnist
    else:
        return None, None

    (x_train, y_train), (x_test, y_test) = dataset.load_data()
    
    # Specify the number of samples you want
    sample_size = 1000  # You can change this to the desired sample size

    # Randomly select a subset of samples for training and testing
    train_indices = np.random.choice(len(x_train), sample_size, replace=False)
    test_indices = np.random.choice(len(x_test), sample_size, replace=False)

    x_train, y_train = x_train[train_indices], y_train[train_indices]
    x_test, y_test = x_test[test_indices], y_test[test_indices]

    # Normalize the pixel values to between 0 and 1
    x_train, x_test = x_train / 255.0, x_test / 255.0
    
    return (x_train, y_train, x_test, y_test)

# CNN model
cnn_model = keras.Sequential([
    keras.layers.Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(28, 28, 1)),
    keras.layers.MaxPooling2D(pool_size=(2, 2)),
    keras.layers.Flatten(),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(10, activation='softmax')
])

cnn_model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

# ANN model
ann_model = keras.Sequential([
    keras.layers.Flatten(input_shape=(28, 28)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(10, activation='softmax')
])

ann_model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

@app.route('/train', methods=['POST'])
def train_model():
    global x_train, y_train  # Indicate that x_train and y_train are global variables
    data = request.get_json()
    model_name = data.get('model_name')
    dataset_name = data.get('dataset_name')

    # Load and preprocess the selected dataset
    x_train, y_train, x_test, y_test = load_and_preprocess_dataset(dataset_name)
    if x_train is None or y_train is None:
        return jsonify({"error": f"Dataset '{dataset_name}' not found."})

    if model_name == 'CNN':
        model = cnn_model
    elif model_name == 'ANN':
        model = ann_model
    else:
        return jsonify({"error": f"Model '{model_name}' not found."})

    # Split the dataset into a training and testing set
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, random_state=42)

    # Train the selected model
    history = model.fit(x_train, y_train, epochs=10, validation_data=(x_val, y_val))

    # Get accuracy and loss values
    accuracy = history.history['accuracy']
    loss = history.history['loss']
    val_accuracy = history.history['val_accuracy']
    val_loss = history.history['val_loss']

    # Calculate y_pred_classes
    y_pred = model.predict(x_val)
    y_pred_classes = np.argmax(y_pred, axis=1)

    # Create plots for accuracy and loss
    fig, axes = plt.subplots(2, 1, figsize=(8, 8))
    axes[0].plot(accuracy, label='Training Accuracy')
    axes[0].plot(val_accuracy, label='Validation Accuracy')
    axes[0].set_title('Accuracy')
    axes[0].legend()
    axes[1].plot(loss, label='Training Loss')
    axes[1].plot(val_loss, label='Validation Loss')
    axes[1].set_title('Loss')
    axes[1].legend()

    # Save the plot to a BytesIO object
    plot_buffer = io.BytesIO()
    plt.savefig(plot_buffer, format='png')
    plot_buffer.seek(0)
    plot_data = base64.b64encode(plot_buffer.read()).decode()

    plt.close()  # Close the plot to free up resources

    # Compute and display the confusion matrix
    labels = unique_labels(y_val, y_pred_classes)
    cm = confusion_matrix(y_val, y_pred_classes, labels=labels)
    cm_dict = {
        "labels": labels.tolist(),
        "matrix": cm.tolist(),
    }

    return jsonify({
        "model_name": model_name,
        "dataset_name": dataset_name,
        "accuracy": accuracy,
        "loss": loss,
        "val_accuracy": val_accuracy,
        "val_loss": val_loss,
        "confusion_matrix": cm_dict,
        "plot_data": plot_data,  # Include the plot data in the response
    })


if __name__ == '__main__':
    app.run(debug=True)
