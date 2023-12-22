import mlflow.sklearn
import numpy as np
run="runs:/4b3be0f7f3644eaa8b56a14fa1e20c37/model"
# Load the model
loaded_model = mlflow.sklearn.load_model(run)

# New data for prediction
new_data = np.array([[5.1, 3.5, 1.4, 0.2], [6.3, 3.3, 6.0, 2.5]])

# Make predictions
predictions = loaded_model.predict(new_data)

print("Predictions:", predictions)
