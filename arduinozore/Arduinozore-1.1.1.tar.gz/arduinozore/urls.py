"""Urls module."""
from arduinozore.handlers.card import CardHandler
from arduinozore.handlers.device import DevicePageHandler
from arduinozore.handlers.index import IndexPageHandler
from arduinozore.handlers.sensor import SensorHandler
from arduinozore.handlers.setting import SettingPageHandler
from arduinozore.handlers.ws import WSHandler
from arduinozore.settings import STATIC_PATH
from tornado.web import StaticFileHandler

url_pattern = [
    (r'/static/(.*)', StaticFileHandler, {'path': STATIC_PATH}),
    (r'/', IndexPageHandler),
    (r'/settings/?$', SettingPageHandler),
    (r'/device/?$', DevicePageHandler),
    (r'/device/((?!create|/)[^/]+)/?$', DevicePageHandler),
    (r'/device/([^/]+)/(?:(edit|create)\w?)?/?', DevicePageHandler),
    (r'/sensor/?$', SensorHandler),
    (r'/sensor/([^/]+)/?$', SensorHandler),
    (r'/sensor/([^/]+)/(?:(edit)\w?)?/?$', SensorHandler),
    (r'/card/?$', CardHandler),
    (r'/card/([^/]+)/?$', CardHandler),
    (r'/card/([^/]+)/(?:(edit)\w?)?/?$', CardHandler),
    (r'/ws/([^/]+)', WSHandler),
]
