import tensorflow as tf
from tensorflow import keras
import joblib
from core.MqttCluster.mqttCluster import MQTTCluster
from core.IPFS.ipfs import IPFS
from tensorflow.keras.callbacks import TensorBoard
import datetime
import subprocess
import webbrowser 
class MLOperations:
    def __init__(self):
        # You can add any necessary initialization code here
        self.ipfs=IPFS()
        self.path_model="saved_model.keras"
        self.path_global_model="global_model.keras"
        self.global_model_hash=None
        self.current_model=None
        pass

    def start_tensorboard(log_dir):
            # Start TensorBoard in the background if it's not running already
        try:
            response = subprocess.check_output(["pgrep", "-f", "tensorboard"]).decode()
            if len(response.split('\n')) == 2:
                subprocess.Popen(["tensorboard", "--logdir", log_dir])
        except subprocess.CalledProcessError:
            subprocess.Popen(["tensorboard", "--logdir", log_dir])
            
    def is_global_model_hash(self,model_hash):    
        self.global_model_hash=model_hash

    def get_data(self):
        (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

                # Preprocess the data
        x_train, x_test = x_train / 255.0, x_test / 255.0

        return x_train, y_train, x_test, y_test
    
    def build_model(self,):
                # Build a simple neural network model
        model = keras.models.Sequential([
            keras.layers.Flatten(input_shape=(28, 28)),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(10)
        ])

        # Compile the model
        model.compile(optimizer='adam',
                      loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                      metrics=['accuracy'])
        

        
        return model


        
        
    def train_machine_learning_model(self):
        """
        This method trains a machine learning model on the MNIST dataset.

        Algorithm:
        1. Load the MNIST dataset.
        2. Preprocess the data.
        3. Build a simple neural network model.
        4. Compile the model with suitable parameters.
        5. Train the model on the training data.
        6. Evaluate the model on the test data.
        7. Save the trained model.

        Returns:
        A message indicating that the machine learning model has been trained with test accuracy and saved.
        """
        # Load the MNIST dataset
        x_train, y_train, x_test, y_test = self.get_data()

        if self.global_model_hash:
            # Get model from IPFS
            self.current_model = self.ipfs.fetch_model(self.global_model_hash)
            print("Model: ", self.current_model)
        else:
            # For the first time, build the model
            self.current_model = self.build_model()

        # Define a log directory for TensorBoard
        log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        # Create a TensorBoard callback
        tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)

        # Train the model with the TensorBoard callback
        self.current_model.fit(x_train, y_train, epochs=2, callbacks=[tensorboard_callback])

        # Evaluate the model on the test data
        test_loss, test_acc = self.current_model.evaluate(x_test, y_test, verbose=2)

        # Save the trained model
        self.current_model.save(self.path_model)

        print(f"Machine learning model trained on MNIST dataset with test accuracy: {test_acc:.2f}. Model saved as {self.path_model}.")

        # Start TensorBoard in the background
        subprocess.Popen(["tensorboard", "--logdir", log_dir])

        # Open the web browser to access TensorBoard
        webbrowser.open("http://localhost:6006")

        hash = self.send_model_to_ipfs(self.path_model)

        print("IPFS Hash: {}".format(hash))

        return hash
    
    def send_model_to_ipfs(self,path):
        return self.ipfs.push_model(path)
        

    def send_model_to_aggregator(self):
        """
        This method represents the action taken when a participant sends their trained model to the aggregator.

        Algorithm:
        1. Prepare the trained model for transmission.
        2. Send the model to the aggregator.

        Returns:
        A message indicating that the model has been sent to the aggregator.
        """
        return "Model sent to the aggregator"

    def aggregator_receives_models(self,):

        """
        This method represents the action taken when the aggregator node receives models from participants.

        Algorithm:
        1. Wait for models to be sent by participants.
        2. Receive and store the models.

        Returns:
        A message indicating that the aggregator has received the models.
        """
        




        return "Aggregator received models"

    def aggregate_models(self,get_model_list):
        """
        This method represents the action taken when the aggregator aggregates received models.

        Algorithm:
        1. Combine and aggregate the received models.
        2. Create a global model using the aggregated information.

        Returns:
        Send Global models to all client.
        """
        # Convert the set to a list

        data=get_model_list

        print("listing models",data)



        models = []
        for value in data:
            # print("vales in loop : ",value)
            model = self.ipfs.fetch_model(value)
            # print("after fetching model : ",model)
            models.append(model)

        # Aggregate model weights
        global_model = self.aggregate_weights(models)

        print("Global model Aggregate weights")

        print("global model ",global_model.summary())

        # Save the trained model
        model.save(self.path_global_model)

        global_model_hash=self.ipfs.push_model(self.path_global_model)

        print("hash global model ",global_model_hash)

        return global_model_hash

        # return "Models aggregated"
    
    def aggregate_weights(self, models):
        # Initialize global model with the architecture of the first model
        global_model = models[0]

        # Iterate through layers and aggregate weights
        for i in range(len(models[0].layers)):
            if 'Dense' in str(models[0].layers[i].get_config()):
                # Extract the weights from all models for this layer
                layer_weights = [model.layers[i].get_weights() for model in models]

                # Calculate the average weights
                average_weights = [sum(w) / len(models) for w in zip(*layer_weights)]

                # Set the average weights to the global model
                global_model.layers[i].set_weights(average_weights)
        
        print("Aggregated weights")

        return global_model

    def is_model_better(self):
        """
        This method checks if the current model is better than the previous one.

        Algorithm:
        1. Compare the performance metrics of the current model with the previous model.
        2. Determine if the current model is better based on defined criteria.

        Returns:
        A message indicating whether the current model is better than the previous one.
        """
        return "Model is better"

    def post_training_steps(self):
        """
        This method represents the completion of post-training steps, which may include additional processes or validations.

        Algorithm:
        1. Execute any post-training steps required by the DFL process.

        Returns:
        A message indicating that post-training steps have been completed.
        """
        return "Post-training steps completed"

    def send_global_model_to_others(self,mqtt_obj,global_model_hash):
        """
        This method represents the action taken when the global model is sent to other participants.

        Algorithm:
        1. Prepare the global model for transmission.
        2. Send the global model to other participants.

        Returns:
        A message indicating that the global model has been sent to others.
        """
        mqtt_obj.send_internal_messages_global_model(global_model_hash)
        return "Global model sent to others"

    def aggregator_saves_global_model_in_ipfs(self):
        """
        This method represents the action taken when the aggregator saves the global model to IPFS.

        Algorithm:
        1. Implement the logic to save the global model to IPFS here.
        2. Return True if the operation is successful, or False otherwise.

        Returns:
        A message indicating the success or failure of saving the global model to IPFS.
        """
        # Implement the logic to save the global model to IPFS here.
        # Return True if the operation is successful, or False otherwise.

        # Placeholder code (replace with the actual implementation)
        print("Aggregator saves the global model to IPFS.")
        return True
