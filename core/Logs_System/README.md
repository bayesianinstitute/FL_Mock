
# Colorful Logger System

This  Logger is a Python logging utility created to capture sensitive events with enhanced console log messages featuring colorful output based on log levels.

## Getting Started

### Installation

To use the Colorful Logger in your project, you can simply copy the `Logger` class from the provided code and include it in your project.

### Usage

1. Import the `Logger` class into your script or module:

    ```python
    from core.Logs_System.logger import Logger
    ```

2. Create an instance of the `Logger` class with an optional name for your logger:

    ```python
    my_logger = Logger(name='my_logger').get_logger()
    ```

3. Use the logger to log messages at different levels:

    ```python
    my_logger.debug("This is a debug message")
    my_logger.info("This is an info message")
    my_logger.warning("This is a warning message")
    my_logger.error("This is an error message")
    my_logger.critical("This is a critical message")
    ```


### Log Levels

The Colorful Logger supports the following log levels:

- `DEBUG`: Detailed information, typically useful for debugging.
- `INFO`: General information about the execution.
- `WARNING`: Indicates a potential issue that does not prevent the program from running.
- `ERROR`: Indicates a more serious issue that might prevent the program from continuing.
- `CRITICAL`: A very serious error that may require immediate attention.

### Log Colors

The console output is colorized for better visibility. Each log level has its own color:

- `DEBUG`: Cyan
- `INFO`: Green
- `WARNING`: Yellow
- `ERROR`: Red
- `CRITICAL`: Red text on a white background

### Customization

You can customize the logger by modifying the `log_colors` dictionary in the `Logger` class. This dictionary maps log levels to their corresponding colors.

```python
log_colors={
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
}
```

Feel free to adjust the colors to your preferences.

---
