import configparser
import os

# Changed 11.04.2018
# Added deprecated, because the 'config_singleton' method was to be re written, but did not want to delete it.
# Added pathlib because for the rewrite of the config_singleton functionality Path objects needed
from deprecated import deprecated
import pathlib


# Changed 11.04.2018
# This function, which was inspired to simplify the creation of config singletons in the ScopusWp project is now
# deprecated, due to me learning how to properly implement singletons in Python using duck typing

@deprecated
def config_singleton(project_path, config_name='config.ini'):
    """
    This function returns a class, which represents a singleton for access to the projects config file. The project
    path and name of the config file are saved to the class by passing them as parameters to the function.

    USAGE:
    In a local project a singleton access class can be created by creating a new class, which inherits from the return
    of this function. And no further methods are needed. The child class can be accessed by calling the 'get_instance'
    method to retrieve the ConfigParser object:

    EXAMPLE:
    Class Config(config_singleton("my/path", "config.ini")): pass
    Config.get_instance()
    # <configparser.ConfigParser>

    :param project_path: The path to the folder where the config file is located
    :param config_name: The string file name of the config file to be subject of the class. DEFAULT: config.ini
    :return: Class:Config
    """
    class Config:
        """
        A singleton class for the access to the config object
        """
        _instance = None

        def __init__(self):
            pass

        @staticmethod
        def get_instance():
            if Config._instance is None:
                Config._instance = Config._create_instance()

            return Config._instance

        @staticmethod
        def _create_instance():
            # Getting the path to the config file
            path = Config._config_path()
            # Creating the config parser object and returning it
            config = configparser.ConfigParser()
            config.read(path)

            return config

        @staticmethod
        def _config_path():
            # Joining the config path
            path = os.path.join(project_path, 'config.ini')
            return path

    return Config


def ConfigBase(path, filename='config.ini'):
    """
    CHANGELOG

    Added 11.04.2018
    Rewrite of the 'config_singleton' function, also a function that returns the base class for a custom config singleton
    but with the class actually being a singleton implemented using python magic methods/duck typing

    CHANGED 15.04.2018
    When using this function to generate a base class for singleton configs, one wants to be able to add constants to
    the config class, which will be used as global variables through out the project. There was a problem with that
    however, where because the get attr method was overwritten for the sake of duck typing, a class variable from the
    singleton class would not be found.
    So to the init of the singleton instance I added a for loop, which will add all upper case attributes of the class
    also as attributes to the singelton instance thus enabling access to those fields.

    Changed 15.04.2018
    Added a folder_path object attribute, which is being used as a parameter of the path function for the derive method
    as that just makes more sense to pass the folder path and filename individually

    :param path:
    :param filename:
    :return:
    """

    class Config:

        class Config:

            def __init__(self):
                self.filename = filename
                self.folder_path = pathlib.Path(path)
                print(str(self.folder_path))
                self.path = self.folder_path / filename
                self.dict = configparser.ConfigParser()
                self.dict.read(str(self.path))

            def load(self):
                self.dict = configparser.ConfigParser()
                self.dict.read(str(self.path))

            def save(self):
                self.dict.write(self.path)

            def __getitem__(self, item):
                return self.dict[item]

            def __setitem__(self, key, value):
                self.dict[key] = value

        _instance = None
        _parent = None

        def __init__(self):
            if self._instance is None:
                config = Config.Config()
                setattr(Config, '_instance', config)
                # Changed 15.04.2018: Adding all the constants, that were added as class fields to the singleton
                # class to the actual singleton instance

                for item in dir(self):
                    if item.isupper():
                        setattr(self._instance, item, getattr(self, item))

        def __getitem__(self, item):
            return self._instance[item]

        def __setitem__(self, key, value):
            self._instance[key] = value

        def __setattr__(self, key, value):
            setattr(self._instance, key, value)

        def __getattr__(self, item):
            return getattr(self._instance, item)

        def derive(self, name, path_function):
            """

            :param name:
            :param path_function:
            :return:
            """
            assert callable(path_function)

            #print(path_function(name, str(self.folder_path), self.filename))
            path, filename = path_function(name, str(self.folder_path), self.filename)
            config = ConfigBase(path, filename)
            setattr(config, '_parent', self._instance)

            return config

        @property
        def parent(self):
            return self._parent

    return Config


