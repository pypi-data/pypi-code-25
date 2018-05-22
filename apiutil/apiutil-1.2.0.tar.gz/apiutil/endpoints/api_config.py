# encoding: utf-8

from future.utils import with_metaclass
from classutils import SingletonType
from classutils.decorators import class_cache_result
from . import (Environments,
               APIS,
               Hosts,
               Endpoints)


class APIConfig(with_metaclass(SingletonType, object)):

    """ API Config provides instances of each of the config classes as cached properties/methods.

    Provided classes:
        --> Environments (property)
        --> APIS (property)
        --> Hosts (property)
        --> Endpoints (method)

    This means they only have to be instantiated once each (increases performance)
    and only one object need be imported in your scripts.

    """

    def __init__(self):
        # Force initialisation!
        _ = self.environments  # This will also init apis & hosts
        _ = self.endpoints

    @property
    @class_cache_result
    def environments(self):
        envs = Environments()
        envs._APIS = self.apis

        return envs

    @property
    @class_cache_result
    def apis(self):
        apis = APIS()
        apis._HOSTS = self.hosts

        return apis

    @property
    @class_cache_result
    def hosts(self):
        return Hosts()

    @property
    @class_cache_result
    def endpoints(self):
        return Endpoints()
