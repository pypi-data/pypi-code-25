# coding: utf-8

from .application import Application
from .monitor import Registry
from .cli import Cli


class Probe(object):

    def __init__(self, config):
        self.registry = Registry(config)

        self.cli = Cli(self.registry, config['DBURI'])
        self.app = Application(self.registry)
        self.app.update_config(config)

    def __call__(self, start_response, environ):
        # make it wsgi compliant
        return self.app(start_response, environ)


__all__ = ['Probe']
