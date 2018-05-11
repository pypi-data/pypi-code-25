# -*- coding: utf-8 -*-

### imports ###################################################################
from flask import Flask

### globals ###################################################################
SERVER_NAME = 'MicroWeb/1.0'

###############################################################################
class VertexFlask(Flask):
    def process_response(self, response):
        response.headers['Content-Type'] = 'text/html'
        response.headers['Last-Modified'] = 'Wed, 20 Sep 2017 14:36:28 GMT'
        response.headers['MIME-Version'] = '1.0'
        response.headers['Server'] = SERVER_NAME
        
        return(response)

###############################################################################
app = VertexFlask(__name__)
app.secret_key = 'development key'

### relative imports from #####################################################
from . import views
