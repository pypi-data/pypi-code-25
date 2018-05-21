import logging
import os
from datetime import datetime

LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FORMAT = '[%(asctime)s] (%(levelname)s) <%(name)s> >> %(message)s'
LOG_ROOT = 'log'
LOG_FILE_FORMAT = '%Y-%m-%d.log'


class LogUtil:
    @staticmethod
    def get_logger(app_name=None, logger_name='yangs_util', is_debug=False):

        log_dir = LogUtil.log_dir(app_name=app_name)
        log_file = LogUtil.log_file()
        log_path = os.path.join(log_dir, log_file)

        # formatter
        formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

        # handler
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG if is_debug is True else logging.INFO)
        sh.setFormatter(formatter)

        # logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        logger.addHandler(sh)

        return logger

    @staticmethod
    def log_dir(app_name):
        tmp_path = ''
        for name_part in app_name.lstrip().rstrip().split(' '):
            tmp_path += name_part + '_'

        log_path = os.path.join(LOG_ROOT, tmp_path[:len(tmp_path) - 1])

        if os.path.isdir(log_path) is False:
            os.makedirs(log_path)

        if os.path.isdir(log_path) is True:
            return log_path
        else:
            return None

    @staticmethod
    def log_file():
        current = datetime.now()
        return current.strftime(LOG_FILE_FORMAT)
