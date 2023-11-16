import logging
import colorlog

class Logger:
    def __init__(self, name='default_logger'):
        self.logger = colorlog.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Create a colorlog stream handler
        handler = colorlog.StreamHandler()

        # Define a formatter with different colors for different log levels
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s [%(levelname)s]%(reset)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        # Set the formatter for the handler
        handler.setFormatter(formatter)

        # Set the logging level for the handler
        handler.setLevel(logging.DEBUG)

        # Add the handler to the logger
        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger

# Example usage:
logger = Logger(name='my_logger').get_logger()

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
