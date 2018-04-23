# coding: utf-8

import os
from flask import send_file
from flask_restful import Resource


def init(api, furl):
    api.add_resource(Document, furl('/document'))
    api.add_resource(ScreenCSS, furl('/stylesheets/screen.css'))
    api.add_resource(PrintCSS, furl('/stylesheets/print.css'))
    api.add_resource(AllJS, furl('/javascripts/all.js'))
    api.add_resource(NavbarPNG, furl('/images/navbar.png'))
    api.add_resource(LogoPNG, furl('/images/logo.png'))

    # api.add_resource(Woff2, furl('/fonts/slate.woff2?-syv14m'))
    # api.add_resource(Woff, furl('/fonts/slate.woff?-syv14m'))
    # api.add_resource(Ttf, furl('/fonts/slate.ttf?-syv14m'))


class Document(Resource):

    def get(self):
        return send_file(os.path.join('doc', 'index.html'))


class ScreenCSS(Resource):

    def get(self):
        return send_file(os.path.join('doc', 'stylesheets', 'screen.css'))


class PrintCSS(Resource):

    def get(self):
        return send_file(os.path.join('doc', 'stylesheets', 'print.css'))


class AllJS(Resource):

    def get(self):
        return send_file(os.path.join('doc', 'javascripts', 'all.js'))


class NavbarPNG(Resource):

    def get(self):
        return send_file(os.path.join('doc', 'images', 'navbar.png'))


class LogoPNG(Resource):

    def get(self):
        return send_file(os.path.join('doc', 'images', 'logo.png'))


class Woff2(Resource):

    def get(self):
        return send_file(os.path.join('doc', 'fonts', 'slate.woff2'))


class Woff(Resource):

    def get(self):
        return send_file(os.path.join('doc', 'fonts', 'nslate.woff'))


class Ttf(Resource):

    def get(self):
        return send_file(os.path.join('doc', 'fonts', 'slate.ttf'))
