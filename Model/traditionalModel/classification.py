from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

class TraditionalModelClassifier:
    def __init__(self):
        self.model = self.build_model()
        self.X, self.y = self.load_and_preprocess_data()

    def build_model(self):
        # Build a simple Random Forest Classifier
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        return model

    def load_and_preprocess_data(self):
        # Load the Iris dataset
        iris = load_iris()
        X = iris.data  # Features
        y = iris.target  # Target labels

        return X, y

    def train_model(self, test_size=0.2):
        # Split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=test_size, random_state=42)

        # Train the model
        self.model.fit(X_train, y_train)

        # Make predictions on the test set
        y_pred = self.model.predict(X_test)

        # Evaluate the model
        accuracy = accuracy_score(y_test, y_pred)
        return accuracy

# Usage example:
if __name__ == '__main__':
    iris_classifier = TraditionalModelClassifier()
    accuracy = iris_classifier.train_model()
    print(f'Test accuracy: {accuracy:.4f}')
