# coding=utf-8
import logging
from time import strftime
from logging.handlers import RotatingFileHandler
import os

application_name = 'user_center'
application_display_name = '用户中心'


class BasicConfig:
    LOG_PATH = 'logs'
    MONGO_USER = ''
    MONGO_PASSWORD = ''
    MONGO_HOST = '127.0.0.1'
    MONGO_PORT = '27017'
    MONGO_DB = 'data_warehouse'

    JWT_SECRET_KEY = ''
    JWT_HEADER_TYPE = 'JWT'
    CRYPTO_KEY = ''


    @classmethod
    def init_app(cls, app):
        if command_args.log_path is not None:
            self.LOG_PATH = command_args.log_path
        config_logging(self.LOG_PATH)
        self.MONGO_URI = 'mongodb://{}:{}@{}:{}'.format(self.MONGO_USER, quote(self.MONGO_PASSWORD), self.MONGO_HOST, self.MONGO_PORT)



def config_logging(log_path):
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    if not log_path.endswith('/'):
        log_path += '/'

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    default_handler = RotatingFileHandler(strftime(log_path + 'log.%Y_%m_%d'), maxBytes=1024 * 1024 * 5,
                                          backupCount=100)
    default_handler.setLevel(logging.INFO)
    default_handler.setFormatter(formatter)
    logger.addHandler(default_handler)

    error_handler = RotatingFileHandler(strftime(log_path + 'error.log.%Y_%m_%d'), maxBytes=1024 * 1024 * 5,
                                        backupCount=100)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
