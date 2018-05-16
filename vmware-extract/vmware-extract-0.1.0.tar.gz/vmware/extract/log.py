import logging.handlers
import logging
import logging.config
import jmespath
from vmware.extract import utils
from path import Path


def configure_logging(name,callback_timestamp):
    settings = utils.load()
    logging_d = jmespath.search('vmware.logging', settings)  # returns dictionary starting from vmware: in conf/yaml file
    if logging_d:
        logging.config.dictConfig(logging_d)

    # set the log filename
    logfilename = Path('{}_{}.log'.format(name,callback_timestamp))

    # set the formatter , by getting it from default yaml
    format_ = jmespath.search('formatters.default.format', logging_d)
    f = logging.Formatter(format_)
    h = logging.FileHandler(logfilename)
    h.setFormatter(f)


    # create the logger
    logger = logging.getLogger(name)

    # Add the handler depending upon value in default config
    if settings['vmware']['enablerotatinglog']:
        h = logging.handlers.RotatingFileHandler(logfilename,
                                                 maxBytes=int(jmespath.search('handlers.rotating.maxBytes', logging_d)),
                                                 backupCount=int(
                                                     jmespath.search('handlers.rotating.backupCount', logging_d)))
        h.setFormatter(f)

    logger.addHandler(h)

    return logger