"""This module is responsible for loading the application configuration."""
import logging
import logging.config
import os

import pytoml


_log = logging.getLogger(__name__)


#: A dictionary of application configuration defaults.
DEFAULTS = dict(
    amqp_url=u'amqp://',
    amqp_to_zmq={
        'queue_name': 'fedmsg_zmq_bridge',
        'bindings': [
            {
                'exchange': u'amq.topic',
                'routing_key': u'#',
                'arguments': {},
            }
        ],
        'publish_endpoint': 'tcp://*:9940',
    },
    zmq_to_amqp={
        'exchange': u'zmq.topic',
        'topics': [u''],
        'zmq_endpoints': [],
    },
    log_config={
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '[%(name)s %(levelname)s] %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            }
        },
        'loggers': {
            'fedmsg_migration_tools': {
                'level': 'INFO',
                'propagate': False,
                'handlers': ['console'],
            },
        },
        # The root logger configuration; this is a catch-all configuration
        # that applies to all log messages not handled by a different logger
        'root': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
    },
)

# Start with a basic logging configuration, which will be replaced by any user-
# specified logging configuration when the configuration is loaded.
logging.config.dictConfig(DEFAULTS['log_config'])


def load(filename=None):
    """
    Load application configuration from a file and merge it with the default
    configuration.

    If the ``FEDMSG_MIGRATION_TOOLS_CONFIG`` environment variable is set to a
    filesystem path, the configuration will be loaded from that location.
    Otherwise, the path defaults to ``/etc/petshop/petshop.toml``.
    """
    config = DEFAULTS.copy()

    if filename:
        config_path = filename
    else:
        config_path = '/etc/fedmsg_migration_tools/config.toml'

    if os.path.exists(config_path):
        _log.info('Loading configuration from {}'.format(config_path))
        with open(config_path) as fd:
            try:
                file_config = pytoml.loads(fd.read())
                for key in file_config:
                    config[key.lower()] = file_config[key]
            except pytoml.core.TomlError as e:
                _log.error('Failed to parse {}: {}'.format(config_path, str(e)))
    else:
        _log.info('The configuration file, {}, does not exist.'.format(config_path))

    return config


class LazyConfig(dict):
    """This class lazy-loads the configuration file."""
    loaded = False

    def __getitem__(self, *args, **kw):
        if not self.loaded:
            self.load_config()
        return super(LazyConfig, self).__getitem__(*args, **kw)

    def get(self, *args, **kw):
        if not self.loaded:
            self.load_config()
        return super(LazyConfig, self).get(*args, **kw)

    def pop(self, *args, **kw):
        if not self.loaded:
            self.load_config()
        return super(LazyConfig, self).pop(*args, **kw)

    def copy(self, *args, **kw):
        if not self.loaded:
            self.load_config()
        return super(LazyConfig, self).copy(*args, **kw)

    def update(self, *args, **kw):
        if not self.loaded:
            self.load_config()
        return super(LazyConfig, self).update(*args, **kw)

    def load_config(self, filename=None):
        self.loaded = True
        self.update(load(filename=filename))
        logging.config.dictConfig(self['log_config'])
        return self


#: The application configuration dictionary.
conf = LazyConfig()
