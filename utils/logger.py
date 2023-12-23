import logging
from termcolor import colored

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.DEBUG:
            return colored(super().format(record), 'light_blue')
        elif record.levelno == logging.INFO:
            return colored(super().format(record), 'light_green')
        elif record.levelno == logging.WARNING:
            return colored(super().format(record), 'yellow')
        elif record.levelno >= logging.ERROR:
            return colored(super().format(record), 'red')
        return super().format(record)

def setup_logger(name, level=logging.INFO, emoji='⚙️'):
    """To setup as many loggers as you want"""

    # Create handlers
    c_handler = logging.StreamHandler()
    c_handler.setLevel(level)

    # Create formatters and add it to handlers
    c_format = ColoredFormatter(emoji + ' | %(name)s | %(message)s')
    c_handler.setFormatter(c_format)

    # Add handlers to the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(c_handler)

    return logger