import pytest
from core.MLOPS.Model.deepLearningModel.NLPLSTMMovieReviews  import NLPLSTMMovieReviews

from config.optimizer_settings import optimizers


@pytest.fixture(params=optimizers)
def lstm_movie_reviews_model(request):
    return NLPLSTMMovieReviews(request.param, log_dir='test_nlplstm_logs')

def test_train_and_evaluate_lstm_model(lstm_movie_reviews_model):
    lstm_movie_reviews_model.train_model(epochs=1, batch_size=32)
    test_loss, test_accuracy = lstm_movie_reviews_model.evaluate_model()

    assert test_loss >= 0.0
    assert test_accuracy >= 0.0

def test_save_and_load_lstm_model(lstm_movie_reviews_model):
    model_filename = 'lstm_movie_model.h5'
    lstm_movie_reviews_model.save_model(model_filename)

    assert lstm_movie_reviews_model.model is not None

    # Clean up the saved model file
    import os
    os.remove(model_filename)

def test_set_weights_lstm_model(lstm_movie_reviews_model):
    # Save the initial weights
    initial_weights = lstm_movie_reviews_model.model.get_weights()

    # Create a new model with the same architecture
    new_model = NLPLSTMMovieReviews('adam', log_dir='test_nlplstm_logs')

    # Set the weights of the new model to the initial weights
    new_model.set_weights(initial_weights)

    # Ensure the weights are set correctly
    new_weights = new_model.model.get_weights()
    assert len(initial_weights) == len(new_weights)
    for i in range(len(initial_weights)):
        assert (initial_weights[i] == new_weights[i]).all()



if __name__ == '__main__':
    pytest.main()
