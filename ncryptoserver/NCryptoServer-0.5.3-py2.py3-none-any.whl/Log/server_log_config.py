# -*- coding: utf-8 -*-
"""
Module which stores an instance of server logger.
"""
import os
import logging

from NCryptoTools.Tools.utilities import compose_log_file_name
from NCryptoTools.Logger.log_config import Logger

# Current nodule folder
LOG_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))

# Path of the server log file
SERVER_LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, compose_log_file_name('server.log'))

# Creates client logger
# "<date-time> <level-of-importance> <module name> <function name> <message>"
client_logger = Logger('server', SERVER_LOG_FILE_PATH,
                       '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s',
                       logging.INFO, logging.INFO)
