import logging


def configure_logging(caller_name: str) -> logging.Logger:
    """
    Configure and retrieve a logger with a specified name.

    This function sets up the logging system with a specific format and info level.
    It then retrieves and returns a logger with the given caller's name.

    :param caller_name: The name of the logger to retrieve. This is typically
                        the name of the module or class using the logger.
    :type caller_name: str
    :return: The configured logger instance for the given name.
    :rtype: logging.Logger

    Example:
        >>> logger = configure_logging("my_module")
        >>> logger.info("This is an info message.")
    """
    # Set up basic logging configuration with a specific format
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Retrieve and return a logger with the specified caller_name
    log = logging.getLogger(caller_name)
    return log
