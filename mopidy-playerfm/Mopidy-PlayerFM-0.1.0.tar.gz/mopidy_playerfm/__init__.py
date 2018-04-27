from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext


__version__ = '0.1.0'

logger = logging.getLogger(__name__)


class PlayerFmExtension(ext.Extension):

    dist_name = 'Mopidy-PlayerFM'
    ext_name = 'playerfm'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(PlayerFmExtension, self).get_config_schema()
        schema['username'] = config.String(optional=True)
        schema['password'] = config.Secret(optional=True)
        schema['refresh_playlists'] = config.Integer(minimum=-1, optional=True)
        return schema

    def setup(self, registry):
        from .backend import PlayerFmBackend
        registry.add('backend', PlayerFmBackend)
