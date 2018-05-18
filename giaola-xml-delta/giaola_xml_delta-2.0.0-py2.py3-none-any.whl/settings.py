#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import logging.config
from os import environ
import sys

# Network settings
NETWORK_CLASS = environ.get('DELTA_NETWORK_CLASS', 'xml_delta.network.Rest')
NETWORK_RETRIES = environ.get('DELTA_NETWORK_RETRIES', 0)
NETWORK_CONNECTION_TIMEOUT = int(environ.get('DELTA_NETWORK_CONNECTION_TIMEOUT', 5))  # seconds
NETWORK_AUTH_HEADER = environ.get('HTTP_AUTH_HEADER', None)
NETWORK_AUTH_KEY = environ.get('HTTP_AUTH_KEY', None)

# Storage settings
STORAGE_CLASS = environ.get('DELTA_STORAGE_CLASS', 'xml_delta.storages.SqlAlchemyStorage')
STORAGE_DATABASE_URL = environ.get('DELTA_STORAGE_DATABASE_URL',
                                   'mysql+cymysql://delta_old:delta_old@localhost:3306/delta_old')

# Parser settings
PARSER_CLASS = environ.get('DELTA_PARSER_CLASS', 'xml_delta.parsers.XMLToDictParser')
PARSER_FLUSH_COUNTER = int(environ.get('DELTA_PARSER_FLUSH_COUNTER', 100))

# Delta settings
DELTA_CLASS = environ.get('DELTA_DELTA_CLASS', 'xml_delta.delta_old.JsonDelta')

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(levelname)s: %(asctime)s %(name)s "%(message)s"'
        },
        'file': {
            'format': '%(levelname)s: %(asctime)s %(name)s "%(message)s"'
        },
        'detailed_file': {
            'format': '%(asctime)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M',
        }
    },
    'handlers': {
        'console': {
            'level': logging.DEBUG,
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        'xml_delta': {
            'level': logging.DEBUG,
            'handlers': [
                'console'
            ]
        },
        'detailed': {
            'level': logging.DEBUG,
            'handlers': []
        }
    }
}

# Add file path handler if LOG_FILE_PATH env variable is set
log_file_path = environ.get('DELTA_LOG_FILE_PATH', None)
log_file_path_detailed = environ.get('DELTA_LOG_FILE_PATH_DETAILED', None)
if log_file_path:
    LOGGING['handlers']['file'] = {
        'level': logging.INFO,
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': log_file_path,
        'when': 'midnight',
        'interval': 1,
        'backupCount': 5,
        'formatter': 'file'
    }
    LOGGING['loggers']['xml_delta']['handlers'].append('file')

if log_file_path_detailed:
    LOGGING['handlers']['detailed_handler'] = {
        'level': logging.INFO,
        'class': 'xml_delta.utils.EnhancedRotatingFileHandler',
        'filename': log_file_path_detailed,
        'when': 'midnight',
        'interval': 1,
        'maxBytes': environ.get('DELTA_LOG_FILE_MAX_BYTES', 200 * 1024),
        'backupCount': environ.get('DELTA_LOG_FILE_BACKUP_COUNT', 5),
        'formatter': 'detailed_file',
    }
    LOGGING['loggers']['detailed']['handlers'].append('detailed_handler')

logging.config.dictConfig(LOGGING)

# Watcher settings
WATCHER_CLASS = environ.get('DELTA_WATCHER_CLASS', 'xml_delta.watchers.FileSystemHandler')
