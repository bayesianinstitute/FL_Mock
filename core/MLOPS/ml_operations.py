
from core.IPFS.ipfs import IPFS
from core.Logs_System.logger import Logger
from core.API.endpoint import *

class MLOperations:
    def __init__(self,training_name_log,ip,training_type,optimizer,training_name='ML_training_name'):
        self.ip=ip
        self.logger=Logger(training_name_log,name='MLOPS_Logger',api_endpoint=f"{self.ip}:8000/{update_logs}").get_logger()
        self.ipfs=IPFS(training_name_log,self.ip)
        self.path_model="saved_model.h5"
        self.path_global_model="global_model.h5"
        self.global_model_hash=None
        self.current_model=None
        self.training_type=training_type
        self.optimizer=optimizer
        self.training_name=training_name
        self.get_weights=None
        
        self.port=5000
        pass



    def is_global_model_hash(self, model_hash):
        try:
            self.global_model_hash = model_hash
        except Exception as e:
            self.logger.error(f"Error in is_global_model_hash: {e}")

    
    def get_model(self,):
        try:

            if self.training_type=='CNN':
                self.logger.info("Loading training model CCN")
                
                from core.MLOPS.Model.deepLearningModel.CNN import CNNMnist

                self.current_model=CNNMnist(self.ip,self.port,self.optimizer,experiment_name=self.training_name,)


            elif self.training_type=='ANN-Regression':
                
                from core.MLOPS.Model.deepLearningModel.ANN_Regression import ANNTabularLinearRegression
                self.current_model=ANNTabularLinearRegression(self.ip,self.port,self.optimizer)

            elif self.training_type=='ANN-Classification':  
                from core.MLOPS.Model.deepLearningModel.ANN_Classification import ANNTabularClassification

                self.current_model=ANNTabularClassification(self.ip,self.port,self.optimizer)
            
            elif self.training_type=='LSTM-(NLP)':
                from core.MLOPS.Model.deepLearningModel.NLP_LSTM import NLPLSTM
                self.current_model=NLPLSTM(self.ip,self.port,self.optimizer,)
            
            elif self.training_type=='LSTM-(TimeSeries)':
                from core.MLOPS.Model.timeSeriesModel.LSTM import TimeSeriesLSTM
                self.current_model=TimeSeriesLSTM(self.ip,self.port,self.optimizer,)

            elif self.training_type=='RNN-(TimeSeries)':
                from core.MLOPS.Model.timeSeriesModel.RNN import TimeSeriesRNN
                self.current_model=TimeSeriesRNN(optimizer=self.optimizer)
            else:
                self.logger.warning("Unknown training and loading CNN Default Training")
                from core.MLOPS.Model.deepLearningModel.CNN import CNNMnist

                self.current_model=CNNMnist(self.optimizer,experiment_name=self.training_name)
            return self.current_model
        except Exception as e:
            self.logger.error(f"Error in get_model: {e}")
            return None

    def train_machine_learning_model(self,rounds=None,epochs=10,batch_size=32):
        try:

            if self.global_model_hash:
                ipfs_model = self.ipfs.fetch_model(self.global_model_hash)

                if ipfs_model is not None:
                    self.get_weights = ipfs_model.get_weights()
                    self.current_model.set_weights(self.get_weights)
                    self.logger.info("Set weights successfully.")
                else:
                    self.logger.error("Failed to fetch model from IPFS. ipfs_model is None.")

            else :
                self.current_model=self.get_model()
                self.current_model.build_model()
                self.logger.info(f"builded model: Successfully built model: {self.current_model}",) 

            
            final_loss, final_accuracy, final_val_loss, final_val_accuracy=self.current_model.train_model(rounds,epochs,batch_size)

            self.current_model.save_model(self.path_model)

            self.logger.info(f'Final Training Loss: {final_loss:.4f}')
            self.logger.info(f'Final Training Accuracy: {final_accuracy:.4f}')
            self.logger.info(f'Final Validation Loss: {final_val_loss:.4f}')
            self.logger.info(f'Final Validation Accuracy: {final_val_accuracy:.4f}')
            hash=self.send_model_to_ipfs(self.path_model)

            return hash,final_accuracy, final_loss,  final_val_accuracy,final_val_loss
        except Exception as e:
            self.logger.error(f"Error in train_machine_learning_model: {e}")
            return None
    
    def send_model_to_ipfs(self, path):
        try:
            return self.ipfs.push_model(path)
        except Exception as e:
            self.logger.error(f"Error in send_model_to_ipfs: {e}")
            return None
        
    def aggregate_models(self,get_model_list:list):
        try:
            if get_model_list is None or len(get_model_list) == 0 or get_model_list[0] is None:
                # Return None in case of None or an empty list
                return None
            data=get_model_list


            models = []
            for value in data:
                model = self.ipfs.fetch_model(value)
                models.append(model)
                
            if len(models)==0:
                return None
            
            global_model = self.aggregate_weights(models)
            self.logger.info("Global model Aggregate weights")
            self.logger.debug(f"global model {global_model.summary()}")
            model.save(self.path_global_model)

            global_model_hash=self.ipfs.push_model(self.path_global_model)

            self.logger.info(f"hash global model {global_model_hash}")

            return global_model_hash

        except Exception as e:
            self.logger.error(f"Error in aggregate_models: {e}")
            return None
    
    def aggregate_weights(self, models):
        try:
            global_model = models[0]

            for i in range(len(models[0].layers)):
                if 'Dense' in str(models[0].layers[i].get_config()):
                    layer_weights = [model.layers[i].get_weights() for model in models]
                    average_weights = [sum(w) / len(models) for w in zip(*layer_weights)]
                    global_model.layers[i].set_weights(average_weights)
            
            self.logger.info("Aggregated weights")

            return global_model
        except Exception as e:
            self.logger.error(f"Error in aggregate_weights: {e}")
            return None

    def send_global_model_to_others(self,mqtt_obj,global_model_hash):
        try:
            mqtt_obj.send_admin_to_client_global_model(global_model_hash)
            return "Global model sent to others"
        except Exception as e:
            self.logger.error(f"Error in send_global_model_to_others: {e}")
            return None

    def aggregator_saves_global_model_in_ipfs(self):
        try:
            self.logger.info("Aggregator saves the global model to IPFS.")
            return True
        except Exception as e:
            self.logger.error(f"Error in aggregator_saves_global_model_in_ipfs: {e}")
            return False


if __name__ == "__main__":
    training_type = 'CNN'  
    optimizer = 'adam' 
    ml_operations = MLOperations(training_type, optimizer)
    global_model_hash = None

    i=0
    while True:
        print("Round : " + str(i))
        print("*"*50)
        i=i+1
        ml_operations.is_global_model_hash(global_model_hash)
        hash1 = ml_operations.train_machine_learning_model()
        hash2 = ml_operations.train_machine_learning_model()
        hash3 = ml_operations.train_machine_learning_model()


        model_list = [hash1, hash2, hash3]
        global_model_hash = ml_operations.aggregate_models(model_list)

        if i==3:
            break
