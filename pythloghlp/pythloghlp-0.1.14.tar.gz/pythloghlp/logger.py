# -*- coding: utf-8 *-*
import logging
import logging.handlers
import json
import os
import pwd
import sys
from datetime import datetime
from . import config
from .dynamodb import DynamoHandler

logger = logging.getLogger(config.Appl)
logger.setLevel(logging.DEBUG)
if os.environ.get('RUNONAWS') == 'true':
    handler = DynamoHandler.to(config.Table,
                               config.Region,
                               config.AccessKeyId,
                               config.SecretAccessKey)
else:    
    handler = logging.handlers.TimedRotatingFileHandler(os.environ.get('LOGPATH') + '/{:%Y-%m-%d}-ieslog.csv'.format(datetime.now()), 
                                                        when='midnight', 
                                                        encoding=None,                                                         
                                                        utc=True)    
    formatter = logging.Formatter('"%(asctime)s";"%(levelname)s";"%(message)s"', '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
logger.addHandler(handler)

def getmeta(meta):
    if os.environ.get('RUNONAWS') == 'true':
        if meta:
            parts = meta.split(';')
            if len(parts) == 3:
                return {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name}), 'Study': parts[0], 'Uid': parts[1], 'Requested': parts[2]}
            else:
                return {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name, 'Data': meta})}
        else:
            return {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name})}
    else:
        return '";"' + config.Appl + '";"' + pwd.getpwuid(os.getuid()).pw_name

def info(str, meta=None):
    if os.environ.get('RUNONAWS') == 'true':
        logger.info(str, extra=getmeta(meta))
    else:
        logger.info(str.replace('\n', ' ') + getmeta(meta))

def debug(str, meta=None):
    if os.environ.get('RUNONAWS') == 'true':
        logger.debug(str, extra=getmeta(meta))
    else:
        logger.debug(str.replace('\n', ' ') + getmeta(meta))

def warning(str, meta=None):
    if os.environ.get('RUNONAWS') == 'true':
        logger.warning(str, extra=getmeta(meta))
    else:
        logger.warning(str.replace('\n', ' ') + getmeta(meta))

def error(str, meta=None):
    if os.environ.get('RUNONAWS') == 'true':
        logger.error(str, extra=getmeta(meta))
    else:
        logger.error(str.replace('\n', ' ') + getmeta(meta))