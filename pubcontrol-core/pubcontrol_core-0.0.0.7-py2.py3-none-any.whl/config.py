from abc import abstractmethod

import os
import pathlib
import configparser
import os
import pathlib
import logging

# Changed 11.04.2018
# Needed the ConfigBase method for the implementation of the Config.sub method
from jutil.configuration import ConfigBase


PROJECT_PATH = pathlib.Path('/home/jonas/PycharmProjects/PubControl/pubcontrol')


class Config(ConfigBase(PROJECT_PATH, 'config.ini')):
    """
    CHANGELOG

    Added 11.04.2018
    Added the method 'sub' which is supposed to be usable, by plugins for the pub control system. The idea is that this
    method returns Config class based on the plugin name and the config class is already based on the config file,
    inside the plugin sub folder of the pubcontrol project folder
    """
    # These are constants, that are relevant to the whole project
    PATH = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
    TEMPLATE_PATH = PATH / 'templates'

    PROJECT_PATH = PROJECT_PATH
    LOGGING_PATH = PROJECT_PATH / 'logs'

    NAME = 'pubcontrol'

    def derive(self, name):
        return super(Config, self).derive(name, Config.path_function)

    @staticmethod
    def path_function(name, path, filename):
        return '{}/{}'.format(path, name), filename


def evaluate_logging_path(config, path_type, path):
    if path_type == 'absolute':
        return path
    elif path_type == 'relative':
        package_path = str(config.PATH)
        return os.path.join(package_path, path)
    elif path_type == 'project':
        project_path = str(config.PROJECT_PATH)
        return os.path.join(project_path, path)
    else:
        raise ValueError('The given path_type is not a valid choice')


class LoggingControllerABC:

    @abstractmethod
    def init(self):
        pass


class SimpleLoggingController(LoggingControllerABC):
    """
    This is the most simple implementation of logging, which will only use a single file, called 'only.log' in the
    logging folder for logs and overwrite it every single time a new session is started
    """
    def __init__(self):
        self.config = Config()

        self.folder_path = pathlib.Path(evaluate_logging_path(
            self.config,
            self.config['LOGGING']['path_type'],
            self.config['LOGGING']['path']
        ))

        self.path = self.folder_path / 'only.log'

    def init(self):
        # Creating the file in case it does not already exist
        if not self.path.exists():
            with self.path.open(mode='w+') as file:
                file.write('\n')

        # Binding the logging module to the file
        logging.basicConfig(
            level=logging.DEBUG,
            filename=str(self.path),
            filemode='w+',
            format='%(asctime)s %(name)-40s %(levelname)-8s %(message)s'
        )


if __name__ == '__main__':
    logging_controller = SimpleLoggingController()
    logging_controller.init()

    logger = logging.getLogger('Hallo')
    logger.warning('TEst')