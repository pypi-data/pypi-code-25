import logging


def create_logger(config, logger_name):
    if config["level"].upper() == "CRITICAL":
        level = logging.CRITICAL
    elif config["level"].upper() == "ERROR":
        level = logging.ERROR
    elif config["level"].upper() == "WARNING":
        level = logging.WARNING
    elif config["level"].upper() == "INFO":
        level = logging.INFO
    elif config["level"].upper() == "DEBUG":
        level = logging.DEBUG
    else:
        raise ValueError("unknown value for logger level ('{}').".format(config["level"]))

    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    if not len(logger.handlers):
        handler = logging.FileHandler(config["file"])
        handler.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
