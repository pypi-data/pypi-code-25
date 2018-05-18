from oslo_config import cfg
from oslo_config import types
import os
from logger_suraj.log import getLogger

# GENERATE THE LOG PATH FROM CURRENT FILE NAME
logpath = '/var/log/'+ os.path.splitext(os.path.basename(__file__))[0] + '.log'

LOG = getLogger(__name__,logpath)

PortType = types.Integer(1, 65535)


def do_register_opts(opts, group=None, ignore_errors=False):
    try:
        cfg.CONF.register_opts(opts, group=group)
        LOG.info("Into function do_register")
    except:
        if not ignore_errors:
            raise


def do_register_cli_opts(opt, ignore_errors=False):
    # TODO: This function has broken name, it should work with lists :/
    if not isinstance(opt, (list, tuple)):
        opts = [opt]
    else:
        opts = opt
    LOG.info("The opts is")
    LOG.info(opts)
    try:
        cfg.CONF.register_cli_opts(opts)
        LOG.info("Calling registercliopts")
    except:
        if not ignore_errors:
            raise

def register_opts(filename,opts,tag,cli_opts=None):
    LOG.info("Into register method")
    LOG.info("The filename is")
    LOG.info(filename)
    do_register_opts(opts, tag)
    LOG.info("Register opts is complete")
# Common CLI options

    if cli_opts:
        do_register_cli_opts(cli_opts)
    cfg.CONF(default_config_files=filename)
    LOG.info("cfg.CONF is")
    LOG.info(cfg.CONF)
    return cfg.CONF





