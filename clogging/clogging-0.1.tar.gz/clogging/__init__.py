"""
A configurable boilerplate for the autologging module. 

Autologging is awesome and is now my go-to for automatic logging
in Python; however, it's not a completely boilerplate free
solution, IMO. This module, logger, addresses two tasks that I
would otherwise need to address in each application:

    * Configurable logging through a configuration file and a
      simple line in the application's initiator.
    * Add funcName to TRACE level output but surpress that
      column for any other level.

Technically clogging could be used to configure the standard
Python logging module, since this doesn't directly interact with
autologging, but it was specifically created to fill in gaps
and save me time building applications that use autologging.
"""

import logging
import logging.handlers
import yaml

def start_from_yaml(conf): 
    """Start logging based on entries in a YAML configuration file.
    All logger entries should be nested under "logger" at the root
    of the YAML file. If this is unclear, look at the example files
    provided. The available settings and defaults are listed under
    _setup_root_logger.

    NOTE: Variables with trailing underscores are Python reserved
    words and are represented in YAML without trailing underscores. 
    """
    with open(conf, 'r') as y_file:
        y = yaml.load(y_file)['logger']

    logger = _setup_root_logger(y)
    return logger

def start_from_args(**kwargs):
    """Start logging based on keyword arguments. This function will
    accept the same options as start_from_yaml.
    """
    logger = _setup_root_logger(kwargs)
    return logger

def _setup_root_logger(y):
    file_ = None
    format_ = '%(asctime)22s - %(levelname)8s - %(name)20s - %(message)s'
    format_ext = '%(asctime)22s - %(levelname)8s - %(name)20s - ' \
                 '%(funcName)20s - %(message)s' 
    level = 'INFO'
    max_file_size = 5000
    max_retention = 5
    verbose_levels = ['TRACE', 'DEBUG']

    if 'level' in y:
        level = y['level']
    if 'format' in y: 
        format_ = y['format']
    if 'format_ext' in y:
        format_ext = y['format_ext']
    if level in verbose_levels: 
        format_ = format_ext
    if 'file' in y:
        file_ = y['file']
        if 'max_file_size' in y:
            max_file_size = y['max_file_size']
        if 'max_retention' in y:
            max_retention = y['max_retention']

    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter(format_)

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if file_:
        fh = logging.handlers.RotatingFileHandler(
                file_,
                maxBytes=max_file_size,
                backupCount=max_retention
        )
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
