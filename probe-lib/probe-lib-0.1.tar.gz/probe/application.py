# coding: utf-8
import os

from flask import Flask
from jinja2 import StrictUndefined
from werkzeug.contrib.fixers import ProxyFix

from .controller import app as controller_app


class Application(Flask):
    jinja_options = {'undefined': StrictUndefined}

    def __init__(self, registry):
        Flask.__init__(self, __name__)

        self.wsgi_app = ProxyFix(self.wsgi_app)
        self.config.update({
            'PROPAGATE_EXCEPTIONS': True
        })

        self.registry = registry
        self.register_blueprint(controller_app)

    def update_config(self, cfg):
        self.config.update(cfg)

        if 'DEBUG' in cfg:
            self.config['DEBUG'] = cfg['DEBUG'].lower() == 'true'
