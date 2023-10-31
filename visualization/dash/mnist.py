import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist

# Load and preprocess the MNIST dataset
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0  # Normalize pixel values to be between 0 and 1

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the web app
app.layout = html.Div([
    html.H1("MNIST Digit Classification with Neural Network"),
    dcc.Graph(id='image-plot'),
    dcc.Slider(
        id='input-slider',
        min=0,
        max=len(x_test) - 1,
        step=1,
        value=0,
        marks={i: str(i) for i in range(0, len(x_test), 500)}
    ),
])

# Define a callback function to update the displayed image and prediction
@app.callback(
    Output('image-plot', 'figure'),
    Input('input-slider', 'value')
)
def update_image_plot(selected_index):
    # Load the selected image
    image = x_test[selected_index]
    
    # Create a neural network model
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10)
    ])

    # Make predictions
    logits = model.predict(np.array([image]))
    predicted_label = np.argmax(logits)

    # Create an image plot
    image_plot = go.Figure()
    image_plot.add_trace(go.Image(z=image, colorscale='gray'))
    image_plot.update_layout(title=f"Predicted Label: {predicted_label}", xaxis_showticklabels=False, yaxis_showticklabels=False)

    return image_plot

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
