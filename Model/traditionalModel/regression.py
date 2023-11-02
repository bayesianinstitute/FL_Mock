from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

class TraditionalModelRegressor:
    def __init__(self):
        self.model = self.build_model()
        self.X, self.y = self.load_and_preprocess_data()

    def build_model(self):
        # Build a simple Random Forest Regressor
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        return model

    def load_and_preprocess_data(self):
        # Load the Diabetes dataset
        diabetes = load_diabetes()
        X = diabetes.data  # Features
        y = diabetes.target  # Target values

        return X, y

    def train_model(self, test_size=0.2):
        # Split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=test_size, random_state=42)

        # Train the model
        self.model.fit(X_train, y_train)

        # Make predictions on the test set
        y_pred = self.model.predict(X_test)

        # Evaluate the model
        mse = mean_squared_error(y_test, y_pred)
        return mse

# Usage example:
if __name__ == '__main__':
    diabetes_regressor = TraditionalModelRegressor()
    mse = diabetes_regressor.train_model()
    print(f'Mean Squared Error: {mse:.4f}')
