import logging
import time


def set_logging(level: int = logging.DEBUG):
    log_format = '%(asctime)s:%(module)s:%(levelname)s: %(message)s'
    logging.basicConfig(format=log_format, level=level,
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.Formatter.converter = time.gmtime

