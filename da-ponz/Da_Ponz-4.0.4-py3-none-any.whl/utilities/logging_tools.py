import logging
import time


def create_logger(file_path):
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s', datefmt='%m/%d/%Y at %I:%M:%S %p:')
    formatter.converter = time.gmtime

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(file_path + 'da_ponz.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger('da_ponz')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def create_sql_logger():
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s', datefmt='%-m/%-d/%Y at %I:%M:%S %p:')
    formatter.converter = time.gmtime

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.INFO)
    sql_logger.addHandler(console_handler)

    return sql_logger


def log_event(event_level, logger, message):
    logger_method = getattr(logger, event_level)
    logger_method(message)
