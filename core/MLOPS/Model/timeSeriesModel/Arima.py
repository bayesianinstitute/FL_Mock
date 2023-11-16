import yfinance as yf
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from tensorflow.keras.callbacks import TensorBoard
import os

class ARIMAModel:
    def __init__(self, ticker, start_date, end_date, order=(1, 1, 1), log_dir='custom_arima_logs'):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.order = order
        self.data = self.load_and_preprocess_data()
        self.model = self.build_arima_model()
        self.log_dir = log_dir

    def load_and_preprocess_data(self):
        data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
        data = data['Close'].values.reshape(-1, 1)
        return data

    def build_arima_model(self):
        model = sm.tsa.ARIMA(self.data, order=self.order)
        model_fit = model.fit()
        return model_fit

    def train_arima_model(self):
        tensorboard_callback = TensorBoard(log_dir=os.path.join(self.log_dir, 'arima'))
        self.model = self.build_arima_model()
        self.model.fit(callbacks=[tensorboard_callback])

    def evaluate_arima_model(self):
        aic = self.model.aic
        bic = self.model.bic
        return aic, bic

    def forecast_arima(self, steps=5):
        forecast = self.model.forecast(steps=steps)
        return forecast


class SARIMAModel:
    def __init__(self, ticker, start_date, end_date, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12), log_dir='sarima_logs'):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.order = order
        self.seasonal_order = seasonal_order
        self.data = self.load_and_preprocess_data()
        self.model = self.build_sarima_model()
        self.log_dir = log_dir

    def load_and_preprocess_data(self):
        data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
        data = data['Close'].values.reshape(-1, 1)
        return data

    def build_sarima_model(self):
        model = SARIMAX(self.data, order=self.order, seasonal_order=self.seasonal_order)
        model_fit = model.fit(disp=False)
        return model_fit

    def train_sarima_model(self):
        tensorboard_callback = TensorBoard(log_dir=os.path.join(self.log_dir, 'sarima'))
        self.model = self.build_sarima_model()
        self.model.fit(callbacks=[tensorboard_callback])

    def evaluate_sarima_model(self):
        aic = self.model.aic
        bic = self.model.bic
        return aic, bic

    def forecast_sarima(self, steps=5):
        forecast = self.model.forecast(steps=steps)
        return forecast


# Usage example:
if __name__ == '__main':
    ticker = "AAPL"
    start_date = "2022-01-01"
    end_date = "2023-01-01"
    arima_order = (1, 1, 1)
    sarima_order = (1, 1, 1, 12)

    arima_model = ARIMAModel(ticker, start_date, end_date, order=arima_order, log_dir='custom_Arima_logs')
    sarima_model = SARIMAModel(ticker, start_date, end_date, order=arima_order, seasonal_order=sarima_order, log_dir='custom_SARIMA_logs')

    arima_model.train_arima_model()
    sarima_model.train_sarima_model()

    aic_arima, bic_arima = arima_model.evaluate_arima_model()
    aic_sarima, bic_sarima = sarima_model.evaluate_sarima_model()

    print(f'ARIMA Model - AIC: {aic_arima:.4f}, BIC: {bic_arima:.4f}')
    print(f'SARIMA Model - AIC: {aic_sarima:.4f}, BIC: {bic_sarima:.4f}')

    arima_forecast_values = arima_model.forecast_arima(steps=5)
    sarima_forecast_values = sarima_model.forecast_sarima(steps=5)

    print("ARIMA Forecast:", arima_forecast_values)
    print("SARIMA Forecast:", sarima_forecast_values)
