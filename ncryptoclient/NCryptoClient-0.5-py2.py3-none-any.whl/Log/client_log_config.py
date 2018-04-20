# -*- coding: utf-8 -*-
"""
Instance of logger for client application
"""
import os
import logging
from NCryptoTools.Logger.log_config import Logger

# Folder of the current module
LOG_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))

# Path of the client log
# CLIENT_LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH,
#                                     utilities.compose_log_file_name('client.log'))
CLIENT_LOG_FILE_PATH = os.path.join(LOG_FOLDER_PATH, 'client.log')

# Creates logger instance with all needed options
client_logger = Logger('client', CLIENT_LOG_FILE_PATH,
                       '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s', 'd',
                       logging.INFO, logging.INFO)

