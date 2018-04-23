# coding: utf-8

import importlib

from flask import Flask
from flask_restful import Api
from flask_restful import Resource

from mlang.config import SERVICE_PORT


app = Flask(__name__)

# 文件的最大大小，2G
# 这里是其中一个限制，Nginx也有一个限制
app.config['MAX_CONTENT_LENGTH'] = 2048 * 1024 * 1024


api = Api(app)


# BASE_URL = '/mlang/api/v1.0'
BASE_URL = '/api/v1.0'


def furl(uri):
    if uri.startswith('/'):
        uri = uri[1:]
    return '%s/%s' % (BASE_URL, uri)


class Version(Resource):
    def get(self):
        return 'v1.0'


api.add_resource(Version, '/')


def import_service(service_name):
    # service = importlib.import_module(service_name, 'mlang_server.service')
    service = importlib.import_module('mlang_server.service.%s' % service_name)
    getattr(service, 'init')(api, furl)


def run():
    import_service('nlp')
    import_service('corpus')
    import_service('vocab')
    import_service('semantic')
    import_service('cluster')
    import_service('sa')
    import_service('w2v')
    import_service('d2v')
    import_service('lm')
    import_service('seq2seq')
    import_service('document')

    app.run(host='0.0.0.0', port=SERVICE_PORT)


if __name__ == '__main__':
    run()

