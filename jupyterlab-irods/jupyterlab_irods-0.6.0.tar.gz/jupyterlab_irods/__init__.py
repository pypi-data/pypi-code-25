"""
Python module to initialize Server Extension & Notebook Extension
"""
from jupyterlab_irods.irods import Irods
from notebook.utils import url_path_join, url_escape
from notebook.base.handlers import APIHandler
import tornado.gen as gen

import re, json


irods = Irods()

class SetupHandler(APIHandler):
    @gen.coroutine
    def post(self, path = ''):
        print(" Post here?")
        body = self.get_json_body()
        print (body)
        irods.set_connection(body)

class IrodHandler(APIHandler):
    @gen.coroutine
    def get(self, path = ''):
        self.finish(json.dumps(irods.get(path)))

    @gen.coroutine
    def put(self, path = ''):
        self.finish(json.dumps(irods.put(path, self.get_json_body())))

    @gen.coroutine
    def delete(self, path = ''):
        self.finish(json.dumps(irods.delete(path)))

    @gen.coroutine
    def patch(self, path = ''):
        self.finish(json.dumps(irods.patch(path, self.get_json_body())))

    @gen.coroutine
    def post(self, path = ''):
        self.finish(json.dumps(irods.post(path, self.get_json_body())))



def _jupyter_server_extension_paths():
    """
    Function to declare Jupyter Server Extension Paths.
    """
    return [{
        'module': 'jupyterlab_irods',
    }]


def _jupyter_nbextension_paths():
    """
    Function to declare Jupyter Notebook Extension Paths.
    """
    return [{"section": "notebook", "dest": "jupyterlab_irods"}]


def load_jupyter_server_extension(nb_server_app):
    """
    Function to load Jupyter Server Extension.
    """
    nb_server_app.log.info("my module enabled!")
    web_app = nb_server_app.web_app
    base_url = web_app.settings['base_url']
    endpoint = url_path_join(base_url, 'irods')
    setup_endpoint = url_path_join(base_url, 'irsetup')
    handlers = [(endpoint + "(.*)", IrodHandler), (setup_endpoint+"(.*)", SetupHandler)]
    web_app.add_handlers('.*$', handlers)
    # irods = Irods()
    # nbapp.web_app.settings['irods'] = irods
    # setup_handlers(nbapp.web_app)