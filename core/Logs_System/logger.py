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
    
    def dump_logs(self, filename):
        # Dump logs to a specified file
        file_handler = logging.FileHandler(filename)
        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)

        # Add the file handler to the logger temporarily for dumping logs
        self.logger.addHandler(file_handler)

        # Dump logs to the file
        self.logger.debug("Dumping logs to file: {}".format(filename))

        # Remove the file handler to avoid duplication in future logs
        self.logger.removeHandler(file_handler)

# Example usage:
loggs = Logger(name='my_custom_logger').get_logger()

loggs.debug("This is a debug message")
loggs.info("This is an info message")
loggs.warning("This is a warning message")
loggs.error("This is an error message")
loggs.critical("This is a critical message")
# Dump logs to a file
loggs.dump_logs('dumped_logs.log')