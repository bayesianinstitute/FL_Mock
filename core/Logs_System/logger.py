import logging
import colorlog
import requests
import json
class DatabaseLogger(logging.Handler):
    def __init__(self, api_endpoint):
        super().__init__()
        self.api_endpoint = api_endpoint

    def emit(self, record):
        log_data = {
            'logs': f"{record.levelname} - {self.format(record)} - {record.filename} - {record.exc_info}",
        }

        print("Log Data:", log_data)  # Add this line for debugging
        try:
            response = requests.put(self.api_endpoint, json=log_data)
            print("Response Status Code:", response.status_code)  # Add this line for debugging

            if response.status_code != 200:
                print(f"Failed to log to API. Status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to log to API. Error: {str(e)}")


class Logger:
    _loggers = {}

    def __new__(cls, name='default_logger', api_endpoint=None):
        if name not in cls._loggers:
            instance = super(Logger, cls).__new__(cls)
            cls._loggers[name] = instance
            return instance
        else:
            return cls._loggers[name]

    def __init__(self, name='default_logger', api_endpoint=None):
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.DEBUG)

            handler = colorlog.StreamHandler()
            formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s [%(levelname)s]%(reset)s: %(message)s - %(filename)s:%(lineno)d',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            handler.setFormatter(formatter)
            handler.setLevel(logging.DEBUG)
            self.logger.addHandler(handler)

            if api_endpoint:
                database_handler = DatabaseLogger(api_endpoint)
                database_handler.setLevel(logging.DEBUG)
                self.logger.addHandler(database_handler)

    def get_logger(self):
        return self.logger

if __name__ == '__main__':
    api_endpoint = "http://127.0.0.1:8000/api/v1/update_logs/"
    logger = Logger(name='my_logger', api_endpoint=api_endpoint).get_logger()

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
