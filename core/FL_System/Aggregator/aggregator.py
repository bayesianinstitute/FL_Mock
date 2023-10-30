import numpy as np

class Model:
    def __init__(self):
        # Initialize your model here
        self.weights = None  # Initialize model weights

    # Your model training and other methods go here

    def get_weights(self):
        # Return the current model weights
        return self.weights

class ModelAggregator:
    def __init__(self):
        self.models = []

    def add_model(self, model):
        # Add a model to the list of models
        self.models.append(model)

    def aggregate_weights(self):
        if len(self.models) == 0:
            raise ValueError("No models to aggregate")

        # Get the weights from each model
        all_weights = [model.get_weights() for model in self.models]

        # Check if all models have the same shape of weights
        shapes = [weights.shape for weights in all_weights]
        if len(set(shapes)) != 1:
            raise ValueError("Model weights have different shapes")

        # Calculate the average of the weights
        aggregated_weights = sum(all_weights) / len(self.models)

        return aggregated_weights

# Usage example:
model1 = Model()
model2 = Model()
model3 = Model()

# Simulate weights for each model (replace with real data)
model1.weights = np.array([1.0, 2.0, 3.0])
model2.weights = np.array([1.5, 2.5, 3.5])
model3.weights = np.array([0.5, 1.5, 2.5])

aggregator = ModelAggregator()
aggregator.add_model(model1)
aggregator.add_model(model2)
aggregator.add_model(model3)

# Aggregate the weights
aggregated_weights = aggregator.aggregate_weights()

# Now you have the aggregated weights in the `aggregated_weights` variable
print("Aggregated Weights:", aggregated_weights)
