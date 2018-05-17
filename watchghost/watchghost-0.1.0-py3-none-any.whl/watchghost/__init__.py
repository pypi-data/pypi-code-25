# WatchGhost, your invisible but loud monitoring pet
# Copyright © 2015 Kozea

import os

from tornado.options import define, options
from tornado.web import Application

define(
    'config', default=os.path.expanduser('~/.config/watchghost'),
    help='configuration folder')
define('debug', default=False, help='debug mode')
define('host', default='localhost', help='server host')
define('port', default=8888, help='server port')
define('secret', default='secret', help='secret key')
define('reload', default=False, help='enable configuration reload')

app = Application(
    debug=options.debug, cookie_secret=options.secret,
    static_path=os.path.join(os.path.dirname(__file__), 'static'),
    template_path=os.path.join(os.path.dirname(__file__), 'templates'))
app.websockets = []
