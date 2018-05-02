from .dev_config import DevelopmentConfig
from .prod_config import ProductionConfig
from .local_config import LocalConfig

profiles = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': LocalConfig
}


def active_config_by_profile(active_profile, command_args):
    global config
    config = profiles[active_profile]
    config.init_config(command_args)
