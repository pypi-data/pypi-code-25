# encoding: utf-8

import logging_helper
from configurationutil import (Configuration,
                               cfg_params)
from ._metadata import __version__, __authorshort__, __module_name__
from ._constants import ReportConstant

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__


def register_report_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=ReportConstant.config.key,
                 config_type=cfg_params.CONST.json,
                 template=ReportConstant.config.template,
                 schema=ReportConstant.config.schema)

    return cfg
