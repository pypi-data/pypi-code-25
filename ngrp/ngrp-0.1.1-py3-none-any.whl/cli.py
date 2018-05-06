from contextlib import contextmanager
import sys

import click

from ngrp import ngrp
from ngrp.config_writer import (ConfigFileExistsError,
                                ConfigLinkConflictError,
                                ConfigLinkExistsError)

FORCE_MESSAGE = "Override existing files."


@click.group()
def reverse_proxy():
    """Nginx HTTP reverse proxy configuration tool."""
    pass


@reverse_proxy.command()
@click.argument("domain")
@click.argument("port")
@click.option("--force", "-f", default=False, is_flag=True, help=FORCE_MESSAGE)
def add(domain, port, force):
    """Add and enable a reverse proxy.
    Redirect DOMAIN traffic to 0.0.0.0:PORT
    """
    with error_handler():
        ngrp.add_http_reverse_proxy(domain, port, force)


@reverse_proxy.command()
@click.argument("domain")
@click.option("--force", "-f", default=False, is_flag=True, help=FORCE_MESSAGE)
def enable(domain, force):
    """Enable proxy for given domain."""
    with error_handler():
        ngrp.enable_http_reverse_proxy(domain, force)


@reverse_proxy.command()
@click.argument("domain")
def disable(domain):
    """Disable proxy for given domain."""
    with error_handler():
        ngrp.disable_http_reverse_proxy(domain)


@reverse_proxy.command()
def reload():
    """Reload nginx configuration."""
    with error_handler():
        ngrp.reload_nginx_config()


@contextmanager
def error_handler():
    try:
        yield
    except ConfigLinkExistsError as e:
        sys.exit("Configuration file link already exists under {}.".format(e.filepath))
    except ConfigFileExistsError as e:
        sys.exit("Configuration file already exists under {}.".format(e.filepath))
    except ConfigLinkConflictError as e:
        sys.exit("{} is not a link.".format(e.filepath))
    except PermissionError as e:
        sys.exit("You don't have write permission to {}.".format(e.filename))
    except ngrp.NginxPermissionError:
        sys.exit("You don't have permission to control nginx runtime.")
    except ngrp.NginxNotFoundError:
        sys.exit("nginx binary not in the $PATH")
