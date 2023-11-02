Tabular Data Analysis and Prediction with Artificial Neural Networks (ANN)
This project demonstrates how to use Artificial Neural Networks (ANNs) with TensorFlow and Keras for tabular data analysis, including both classification and linear regression tasks. It includes two different classes: ANNTabularClassification for classification tasks and ANNTabularLinearRegression for linear regression tasks.

Table of Contents
Introduction
Requirements
Usage - Classification
Usage - Linear Regression
Customization
License
Introduction
Artificial Neural Networks (ANNs) are a versatile tool for solving various data analysis and prediction tasks. This project showcases how to use ANNs to analyze and predict tabular data. It includes two different classes, one for classification tasks and another for linear regression tasks.

Requirements
Before using this project, make sure you have the following dependencies installed:

TensorFlow
NumPy
scikit-learn (for data preprocessing)
Pandas (for data manipulation)
For running TensorBoard:
TensorBoard (for visualization)
You can install these libraries using pip:

bash
Copy code
pip install tensorflow numpy scikit-learn pandas
Usage - Classification
To use this project for classification tasks, follow these steps:

Clone or download this repository.

Open a terminal and navigate to the project directory.

Open a Python environment or IDE of your choice.

Run the ANNTabularClassification class with the desired configuration. This class is designed for classification tasks, and you can set the optimizer (e.g., 'adam').

```python
if __name__ == '__main__':
    tabular_model = ANNTabularClassification('adam')
    tabular_model.train_model(epochs=10, batch_size=32)
    test_loss, test_accuracy = tabular_model.evaluate_model()
    print(f'Test loss: {test_loss:.4f}, Test accuracy: {test_accuracy:.4f}')

    tabular_model.run_tensorboard()

```
The model will be trained on the specified data for classification tasks, and you can evaluate its performance.
Usage - Linear Regression
To use this project for linear regression tasks, follow these steps:

Uncomment the linear regression part in the provided code (inside if __name__ == '__main__':).

Clone or download this repository.

Open a terminal and navigate to the project directory.

Open a Python environment or IDE of your choice.

Run the ANNTabularLinearRegression class with the desired configuration. This class is designed for linear regression tasks, and you can set the optimizer (e.g., 'adam').

```
if __name__ == '__main__':
    tabular_regression_model = ANNTabularLinearRegression('adam')
    tabular_regression_model.train_model(epochs=10, batch_size=32)
    test_loss, test_mae = tabular_regression_model.evaluate_model()
    print(f'Test loss: {test_loss:.4f}, Test Mean Absolute Error: {test_mae:.4f}')

    tabular_regression_model.run_tensorboard()

```
The model will be trained on the specified data for linear regression tasks, and you can evaluate its performance.
Customization
You can customize the project by modifying the ANN architecture, changing the optimizer, and specifying different hyperparameters in the classes (ANNTabularClassification and ANNTabularLinearRegression). You can also customize the TensorBoard log directory for better visualization.