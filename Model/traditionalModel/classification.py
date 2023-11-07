import mlflow
import mlflow.sklearn
from sklearn.datasets import load_breast_cancer  # Change the dataset import
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

class TraditionalModelClassifier:
    def __init__(self):
        self.model = self.build_model()
        self.X, self.y = self.load_and_preprocess_data()

    def build_model(self):
        # Build a simple Random Forest Classifier
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        return model

    def load_and_preprocess_data(self):
        # Load the Breast Cancer dataset (change to the new dataset)
        data = load_breast_cancer()
        X = data.data  # Features
        y = data.target  # Target labels

        return X, y

    def train_model(self, test_size=0.2):
        # Split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=test_size, random_state=42)

        # Start an MLflow run
        with mlflow.start_run():
            # Train the model
            self.model.fit(X_train, y_train)

            # Make predictions on the test set
            y_pred = self.model.predict(X_test)

            # Evaluate the model
            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')

            # Log metrics using MLflow
            mlflow.log_metrics({
                "accuracy": accuracy,
                "f1_score": f1,
                "precision": precision,
                "recall": recall
            })

            # Log additional parameters using MLflow
            mlflow.log_params({
                "n_estimators": self.model.n_estimators,
                "test_size": test_size
            })

        return accuracy

if __name__ == '__main__':
    breast_cancer_classifier = TraditionalModelClassifier()  # Rename the classifier object
    accuracy = breast_cancer_classifier.train_model()  # Rename the classifier object

    print(f'Test accuracy: {accuracy:.4f}')
