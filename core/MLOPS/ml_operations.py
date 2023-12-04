
from core.IPFS.ipfs import IPFS
from core.Logs_System.logger import Logger

class MLOperations:
    def __init__(self,training_type,optimizer):
        # You can add any necessary initialization code here
        self.logger=Logger(name='MLOPSs_Logger').get_logger()
        self.ipfs=IPFS()
        self.path_model="saved_model.h5"
        self.path_global_model="global_model.h5"
        self.global_model_hash=None
        self.current_model=None
        self.training_type=training_type
        self.optimizer=optimizer
        self.get_weights=None
        pass

    def is_global_model_hash(self,model_hash):    
        self.global_model_hash=model_hash

    
    def get_model(self,):
                # Build a simple neural network model

        if self.training_type=='CNN':
            
            from core.MLOPS.Model.deepLearningModel.CNN import CNNMnist

            self.current_model=CNNMnist(self.optimizer)


        elif self.training_type=='ANN-Regression':
            
            from core.MLOPS.Model.deepLearningModel.ANN import ANNTabularLinearRegression
            self.current_model=ANNTabularLinearRegression(self.optimizer)

        elif self.training_type=='ANN-Classification':  
            from core.MLOPS.Model.deepLearningModel.ANN import ANNTabularClassification

            self.current_model=ANNTabularClassification(self.optimizer)
        
        elif self.training_type=='LSTM-(NLP)':
            from core.MLOPS.Model.deepLearningModel.NLPLSTMMovieReviews import NLPLSTMMovieReviews
            self.current_model=NLPLSTMMovieReviews(optimizer=self.optimizer,)
        
        elif self.training_type=='LSTM-(TimeSeries)':
            from core.MLOPS.Model.timeSeriesModel.LSTM import TimeSeriesLSTM
            self.current_model=TimeSeriesLSTM(optimizer=self.optimizer,)

        elif self.training_type=='RNN-(TimeSeries)':
            from core.MLOPS.Model.timeSeriesModel.RNN import TimeSeriesRNN
            self.current_model=TimeSeriesRNN(optimizer=self.optimizer)
        
       



        
        return self.current_model
        

    def train_machine_learning_model(self):

        # Check if the global model hash is available
        if self.global_model_hash:


            # get model from ipfs
            ipfs_model=self.ipfs.fetch_model(self.global_model_hash)


            # self.logger.info(" model: ", self.current_model)
            self.get_weights=ipfs_model.get_weights()

            # self.logger.info("getti Weight: ", self.get_weights[0])

            self.current_model.set_weights(self.get_weights)

            
            self.logger.info("set Weight Successfully ")

        else :
            # For First time build model
            self.current_model=self.get_model()
            self.current_model.build_model()
            self.logger.info(f"builded model: Successfully built model: {self.current_model}",) 
            import time
            time.sleep(5)
        

        # Train the model
        self.current_model.train_model(epochs=1,batch_size=32)

        # Show Ui
        # self.current_model.run_tensorboard()

        # Evaluate the model on the test data
        test_loss, test_acc = self.current_model.evaluate_model()

        # Save the trained model
        self.current_model.save_model(self.path_model)

        self.logger.info(f"Machine learning model trained on MNIST dataset with test accuracy: {test_acc:.2f}. Model saved as {self.path_model}.")

        hash=self.send_model_to_ipfs(self.path_model)

        return hash,test_acc,test_loss
    
    def send_model_to_ipfs(self,path):
        return self.ipfs.push_model(path)
        
    def aggregate_models(self,get_model_list:list):
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

        self.logger.info(f"listing models {data}")



        models = []
        for value in data:
            # self.logger.info("vales in loop : ",value)
            model = self.ipfs.fetch_model(value)
            # self.logger.info("after fetching model : ",model)
            models.append(model)

        # Aggregate model weights
        global_model = self.aggregate_weights(models)

        self.logger.info("Global model Aggregate weights")

        self.logger.debug(f"global model {global_model.summary()}")

        # Save the trained model
        model.save(self.path_global_model)

        global_model_hash=self.ipfs.push_model(self.path_global_model)

        self.logger.info(f"hash global model {global_model_hash}")

        return global_model_hash

    
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
        
        self.logger.info("Aggregated weights")

        return global_model

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
        self.logger.info("Aggregator saves the global model to IPFS.")
        return True


if __name__ == "__main__":
        # Create an instance of MLOperations
    training_type = 'CNN'  # Choose the appropriate training type
    optimizer = 'adam'  # Choose the optimizer
    ml_operations = MLOperations(training_type, optimizer)

    # Set the global model hash if available
    global_model_hash = None

    i=0
    while True:
        print("Round : " + str(i))
        print("*"*50)
        i=i+1

        # Check global model hash
        ml_operations.is_global_model_hash(global_model_hash)

        # Train a machine learning model
        hash1 = ml_operations.train_machine_learning_model()
        hash2 = ml_operations.train_machine_learning_model()
        hash3 = ml_operations.train_machine_learning_model()





        # Aggregate models 
        model_list = [hash1, hash2, hash3]
        global_model_hash = ml_operations.aggregate_models(model_list)

        if i==3:
            break

        '''
        # Require Mqtt Object 

        # Send the global model to others (replace mqtt_obj with your MQTT implementation)
        mqtt_obj = YourMQTTClass()
        result = ml_operations.send_global_model_to_others(mqtt_obj, global_model_hash)

        # self.logger.info the result
        self.logger.info(result)
        
        '''

