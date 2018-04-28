#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent
    ~~~~~~~~~~~~

    This module is the main config.

    :copyright: (c) 2017 by Ma Fei.
"""
import os
from logging.config import dictConfig

from agent.config import sentry_env_url

if "AGENT_ENV" in os.environ:
    dsn = sentry_env_url[os.environ["AGENT_ENV"]]
else:
    print('AGENT_ENV not found in Environment change to alpha')
    os.environ['AGENT_ENV'] = 'alpha'
    dsn = sentry_env_url['alpha']

__version__ = '348'

LOGGING_CONFIG = dict({
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'qpagent': {
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': dsn,
        },
    },
    'formatters': {
        'console': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s '
                      '%(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%H:%M:%S',
        },
    }
})
dictConfig(LOGGING_CONFIG)
