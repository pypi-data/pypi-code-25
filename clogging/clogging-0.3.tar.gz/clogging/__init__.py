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

import bitmath
import logging
import logging.handlers
import yaml

def start_from_yaml(conf): 
    """Start logging based on entries in a YAML configuration file.
    All clogging entries should be nested under "clogging" at the
    root of the YAML file. For example:
      
      clogging:
        file: log/app.log
        format: "%(asctime)22s - %(levelname)8s - %(name)20s - %(message)s"
        format_ext: "%(asctime)22s - %(levelname)8s - %(name)20s - " \
                "%(funcName)20s - %(message)s"
        level: INFO
        max_file_size: 5 MB
        max_retention: 5
        verbose_levels: ['TRACE', 'DEBUG']
    
    All settings are optional. If you erase one or more of the
    settings in the YAML file, default settings will be used. 
    
    NOTE: This function does require that you have at least the
    "clogging" section in your YAML file.
    
    See documentation for additional info.
    """
    try:
        with open(conf, 'r') as y_file:
            y = yaml.load(y_file)['clogging']
    except KeyError:
        raise KeyError("clogging entry was not found in %s" %(conf))

    logger = _setup_root_logger(y)
    return logger

def start_from_args(**kwargs):
    """Start logging based on keyword arguments. This function will
    accept the same options as start_from_yaml. For example:
    
    log = clogging.start_from_args(
            file="log/app.log",
            format="%(asctime)22s - %(levelname)8s - %(name)20s - %(message)s",
            format_ext: "%(asctime)22s - %(levelname)8s - %(name)20s - " \
                        "%(funcName)20s - %(message)s",
            level=INFO,
            max_file_size="5 MB",
            max_retention=5,
            verbose_levels=['TRACE', 'DEBUG']
    )

    All settings are optional. If you remove one or more of the
    keywork parameters, their default settings will be used. See
    documentation for additional info.
    """
    logger = _setup_root_logger(kwargs)
    return logger

def _setup_root_logger(y):
    """Configure and return the root Logger instance.
    
    Variables with trailing underscores are Python reserved words
    and are represented in YAML WITHOUT trailing underscores. 
    """
    file_ = None
    format_ = '%(asctime)22s - %(levelname)8s - %(name)20s - %(message)s'
    format_ext = '%(asctime)22s - %(levelname)8s - %(name)20s - ' \
                 '%(funcName)20s - %(message)s' 
    level = 'INFO'
    max_file_size = '5 MB'
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
            try: # Convert value to bytes
                max_file_size = int(
                    bitmath.parse_string(y['max_file_size']).bytes
                )
            except ValueError: # Value is supplied is in bytes
                max_file_size = int(y['max_file_size'])
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
