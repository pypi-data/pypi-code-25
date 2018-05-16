# encoding=utf-8
from __future__ import absolute_import

import logging
import logging.config

from dandan import value

def getLogger(name="dandan", level=logging.DEBUG, filename=None, backup_count=10):
    '''
    Get logger for convenient method

    Args:
        * name (string): logger name, default as 'dandan'
        * level (logger level, optional): level of this logger such as DEBUG, INFO, WARNING, ERROR, FATAL
        * filename (string, optional): filename for timerotedlogger
        * backup_count (int, optional): file backup count, if file count larger than count, then oldest file will be deleted.

    Returns:
        * logger: the logger named name
    '''

    logger = logging.getLogger(name)
    if len(logger.handlers) > 0:
        return logger
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '[%(asctime)s] [%(module)s] [%(lineno)d] [%(levelname)s] | %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                "level": "DEBUG",
            },
            'null': {
                'class': 'logging.NullHandler',
            },
        },
        'loggers': {
            name: {
                'handlers': ['console', ],
                'level': level,
                'propagate': True,
            },
        },
    }
    config = value.AttrDict(config)
    if filename:
        config.handlers.file = {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'filename': filename,
            'when': "MIDNIGHT",
            "level": "INFO",
            "backupCount": backup_count,
            "encoding": "utf8",
        }
        config.loggers[name].handlers.append("file")

    logging.config.dictConfig(config)

    logger = logging.getLogger(name)
    for handler in logger.handlers:
        if handler.name != "file":
            continue
        if handler.suffix != "%Y-%m-%d.log":
            handler.suffix = "%Y-%m-%d.log"

    return logger
