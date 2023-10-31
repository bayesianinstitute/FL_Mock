import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import tensorflow as tf
import numpy as np
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions
from tensorflow.keras.preprocessing import image
import requests
from PIL import Image
from io import BytesIO
import base64  # Add this import

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the web app
app.layout = html.Div([
    html.H1("CNN Image Classifier (VGG16)"),
    dcc.Upload(
        id='upload-image',
        children=html.Div(['Drag and Drop or ', html.A('Select an Image')]),
        multiple=False
    ),
    html.Div(id='output-image-upload'),
    dcc.Graph(id='prediction-bar-chart')
])

# Load the VGG16 model
model = VGG16(weights='imagenet')

# Define a callback function to process image and make predictions
@app.callback(
    Output('output-image-upload', 'children'),
    Output('prediction-bar-chart', 'figure'),
    Input('upload-image', 'contents')
)
def update_output(content):
    if content is None:
        raise PreventUpdate

    # Decode the uploaded image
    content_type, content_string = content.split(',')
    image_bytes = BytesIO(base64.b64decode(content_string))
    img = Image.open(image_bytes)
    img = img.resize((224, 224))  # VGG16 input size

    # Preprocess the image for VGG16 model
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)

    # Make predictions using the VGG16 model
    predictions = model.predict(img)
    decoded_predictions = decode_predictions(predictions, top=5)[0]

    # Create a bar chart for predictions
    classes, scores = zip(*decoded_predictions)
    bar_chart = go.Figure(data=[go.Bar(x=scores, y=classes, orientation='h')])
    bar_chart.update_layout(title="Top 5 Predictions", xaxis_title="Probability", yaxis_title="Class")

    return html.Img(src=content, style={'width': '100%'}), bar_chart

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
