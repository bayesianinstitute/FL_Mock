class ModelEvaluator:
    def __init__(self, current_model, previous_model):
        self.current_model = current_model
        self.previous_model = previous_model

    def evaluate_model(self, model):
        # Simulated evaluation logic (replace this with your actual evaluation logic)
        return model.accuracy

    def is_model_better(self):
        current_performance = self.evaluate_model(self.current_model)
        previous_performance = self.evaluate_model(self.previous_model)

        if current_performance > previous_performance:
            return "Current model is better"
        else:
            return "Previous model is better"

def main():
    # Simulated model instances with an accuracy attribute
    current_model = Model(0.85)  # Replace with your model
    previous_model = Model(0.78)  # Replace with your previous model

    evaluator = ModelEvaluator(current_model, previous_model)
    result = evaluator.is_model_better()
    print(result)

class Model:
    def __init__(self, accuracy):
        self.accuracy = accuracy

if __name__ == "__main__":
    main()
