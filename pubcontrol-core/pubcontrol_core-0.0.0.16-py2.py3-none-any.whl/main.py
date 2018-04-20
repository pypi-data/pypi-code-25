from pubcontrol.plugin import hookspec, PluginManager
from pubcontrol.config import Config

from pubcontrol.register import DictPublicationBuilder
from pubcontrol.database import MySQLDatabase
from pubcontrol.register import PublicationRegister
from pubcontrol.config import SimpleLoggingController
from pubcontrol.plugin import PluginLoader
from pubcontrol.hook import *

from jutil.logging import LogFileObserver

from pprint import pprint

import logging


class Pubcontrol:

    def __init__(self,
                 logging_controller_class=SimpleLoggingController,
                 register_class=PublicationRegister,
                 plugin_loader_class=PluginLoader,
                 publication_builder_class=DictPublicationBuilder,
                 database_singleton_class=MySQLDatabase
                 ):
        # It is important that the logging is created first there, because nothing can be logged before this is not
        # initialized
        self.logging_controller = logging_controller_class()
        self.logging_controller.init()

        self.config = Config()
        self.logger = logging.getLogger(self.config.NAME)

        self.register = register_class(publication_builder_class, database_singleton_class)
        self.plugin_loader = plugin_loader_class()

        self.config = Config()
        self.pm = PluginManager()

        # Loading all the plugins
        self.plugin_loader.load()
        self.logger.info('[Top] Pubcontrol init finalized')

    def fetch(self):
        """
        CHANGELOG

        Changed 14.04.2018
        Added a query, that checks if the publication in the same origin context and with the given origin id already
        exists before inserting it into the database.
        This is not to insert duplicate entries into the database

        :return:
        """
        print(self.pm.hook.fetch(register=self.register))
        for publication_dict_generator in self.pm.hook.fetch(register=self.register):
            self.logger.info('[fetch] Starting a new generator')
            for publication_dict in publication_dict_generator:

                # Inserting the the publication only if there is no collision for the origin id
                origin_type = publication_dict['origin']['name']
                origin_name = publication_dict['origin']['id']
                if len(self.register.select_by_origin(origin_type, origin_name)) == 0:
                    self.register.insert_publication(publication_dict)

    def process(self):
        self.pm.hook.process(register=self.register)


PluginManager().add_module(__name__)


def main():
    from pubcontrol.database import MySQLDatabase
    from pubcontrol.register import BASE
    import importlib

    def create_all():
        plugin_loader = PluginLoader()
        plugin_loader.load()
        module_names = PluginManager().hook.model_module()
        print(module_names)
        for module_name in module_names:
            importlib.import_module(module_name)
        MySQLDatabase().create_all(BASE)

    #create_all()

    p = Pubcontrol()

    o = LogFileObserver('/home/jonas/PycharmProjects/PubControl/pubcontrol/logs/only.log')
    def f(x):
        if (' scopus ' in x or ' pubcontrol ' in x or ' wordpress ') and '[Web]' not in x and 'HTTP' not in x:
            print(x[:-1])
    o.add_callback(f)
    o.start()

    p.fetch()
    p.process()

if __name__ == '__main__':
    main()