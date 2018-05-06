import subprocess

from ngrp.config_writer import ConfigWriter
from ngrp.templates import HttpReverseProxyTemplate


def add_http_reverse_proxy(domain, port, force):
    template = HttpReverseProxyTemplate()
    config_writer = ConfigWriter(domain)
    config_str = template.format(domain=domain, port=port)
    config_writer.write(config_str, force=force)


def enable_http_reverse_proxy(domain, force):
    config_writer = ConfigWriter(domain)
    config_writer.enable_config(force=force)


def disable_http_reverse_proxy(domain):
    config_writer = ConfigWriter(domain)
    config_writer.disable_config()


def reload_nginx_config():
    try:
        nginx_out = subprocess.run("/usr/sbin/nginx -s reload".split(), stderr=subprocess.PIPE)
        nginx_out.check_returncode()
    except FileNotFoundError:
        raise NginxNotFoundError
    except subprocess.CalledProcessError:
        raise NginxPermissionError


class NginxNotFoundError(BaseException):
    pass


class NginxPermissionError(BaseException):
    pass
