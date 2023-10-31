import dash
import dash_core_components as dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from sklearn.linear_model import LinearRegression

# Sample data
data = pd.DataFrame({'X': [1, 2, 3, 4, 5], 'Y': [2, 4, 3, 5, 6]})

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the web app
app.layout = html.Div([
    html.H1("Linear Regression Model"),
    dcc.Graph(id='scatter-plot'),
    dcc.Slider(
        id='input-slider',
        min=1,
        max=5,
        step=1,
        value=1,
        marks={i: str(i) for i in range(1, 6)}
    ),
])

# Define a callback function to update the scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    Input('input-slider', 'value')
)
def update_scatter_plot(selected_value):
    # Fit a linear regression model
    model = LinearRegression()
    model.fit(data[['X']][:selected_value], data['Y'][:selected_value])

    # Predict Y values
    predicted_y = model.predict(data[['X']])

    # Create a scatter plot
    scatter_plot = go.Figure(data=[
        go.Scatter(x=data['X'], y=data['Y'], mode='markers', name='Actual Data'),
        go.Scatter(x=data['X'], y=predicted_y, mode='lines', name='Regression Line'),
    ])

    scatter_plot.update_layout(title="Linear Regression", xaxis_title="X", yaxis_title="Y")

    return scatter_plot

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
