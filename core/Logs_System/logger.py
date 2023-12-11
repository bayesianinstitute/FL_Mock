import logging
import colorlog

class Logger:
    _loggers = {}  

    def __new__(cls, name='default_logger'):
        if name not in cls._loggers:
            instance = super(Logger, cls).__new__(cls)
            cls._loggers[name] = instance
            return instance
        else:
            return cls._loggers[name]

    def __init__(self, name='default_logger'):
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

    def get_logger(self):
        return self.logger


if __name__ == '__main__':
    logger = Logger(name='my_logger').get_logger()

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
