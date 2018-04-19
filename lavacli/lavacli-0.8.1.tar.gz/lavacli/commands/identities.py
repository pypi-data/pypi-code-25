# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2018 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

import os
import yaml


class ConfigurationError(Exception):
    pass


def configure_parser(parser, version):
    sub = parser.add_subparsers(dest="sub_sub_command", help="Sub commands")
    sub.required = True

    # "add"
    config_add = sub.add_parser("add", help="add an identity")
    config_add.add_argument("id", type=str, help="identity")
    config_add.add_argument("--uri", type=str, required=True,
                            help="URI of the lava-server RPC endpoint")
    config_add.add_argument("--username", type=str, default=None,
                            help="api username")
    config_add.add_argument("--token", type=str, default=None,
                            help="api token")
    config_add.add_argument("--proxy", type=str, default=None,
                            help="http proxy")

    # "delete"
    config_del = sub.add_parser("delete", help="delete an alias")
    config_del.add_argument("id", help="identity")

    # "list"
    config_list = sub.add_parser("list", help="list available identities")

    # "show"
    config_show = sub.add_parser("show", help="show identity details")
    config_show.add_argument("id", type=str, help="identity")

    # "version"
    config_version = sub.add_parser("version", help="expected version")
    vers_sub = config_version.add_subparsers(dest="sub_sub_sub_command",
                                             help="Sub commands")
    vers_sub.required = True
    vers_check = vers_sub.add_parser("check",
                                     help="check version")
    vers_check.add_argument("id", type=str, help="identity")

    vers_upgrade = vers_sub.add_parser("upgrade",
                                       help="upgrade to server version")
    vers_upgrade.add_argument("id", type=str, help="identity")


def help_string():
    return "manage lavacli configuration"


def _load_configuration():
    config_dir = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    config_filename = os.path.expanduser(os.path.join(config_dir,
                                                      "lavacli.yaml"))

    try:
        with open(config_filename, "r", encoding="utf-8") as f_conf:
            data = yaml.load(f_conf.read())
            if not isinstance(data, dict):
                raise ConfigurationError("Invalid configuration file")
            return data
    except (FileNotFoundError, KeyError, TypeError):
        return {}


def _save_configuration(config):
    config_dir = os.environ.get("XDG_CONFIG_HOME", "~/.config")
    config_filename = os.path.expanduser(os.path.join(config_dir,
                                                      "lavacli.yaml"))

    with open(config_filename, "w", encoding="utf-8") as f_conf:
        f_conf.write(yaml.dump(config, default_flow_style=False).rstrip("\n"))


def handle_add(proxy, options):
    config = _load_configuration()
    config[options.id] = {"uri": options.uri}
    if options.proxy:
        config[options.id]["proxy"] = options.proxy
    if options.username:
        config[options.id]["username"] = options.username
    if options.token:
        config[options.id]["token"] = options.token

    _save_configuration(config)


def handle_delete(proxy, options):
    config = _load_configuration()
    del config[options.id]
    _save_configuration(config)


def handle_list(proxy, option):
    config = _load_configuration()
    print("Identities:")
    for identity in sorted(config.keys()):
        print("* %s" % identity)


def handle_show(proxy, options):
    config = _load_configuration()
    try:
        conf_str = yaml.dump(config[options.id], default_flow_style=False)
        print(conf_str.rstrip('\n'))
    except KeyError:
        print("Unknown identity '%s'" % options.id)
        return 1


def handle_version(proxy, options):
    if options.sub_sub_sub_command == "check":
        config = _load_configuration()
        if config.get(options.id) is None:
            print("Unknown identity '%s'" % options.id)
            return 1

        config_version = config[options.id].get("version")
        server_version = proxy.system.version()

        print("config: %s" % config_version)
        print("server: %s" % server_version)
        return config_version != server_version
    else:
        config = _load_configuration()
        if config.get(options.id) is None:
            print("Unknown identity '%s'" % options.id)
            return 1
        version = proxy.system.version()
        config[options.id]["version"] = version
        print("server: %s" % version)
        _save_configuration(config)


def handle(proxy, options, _):
    handlers = {
        "add": handle_add,
        "delete": handle_delete,
        "list": handle_list,
        "show": handle_show,
        "version": handle_version
    }
    return handlers[options.sub_sub_command](proxy, options)
