# -*- coding: utf-8 -*-
# Copyright 2018 IFOOTH
# Author: Joe Lei <thezero12@hotmail.com>
import logging.config
import os.path

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'httplog': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.expanduser('~') + '/httplog.log',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'httplog': {
            'handlers': ['httplog'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}

logging.config.dictConfig(LOGGING)
