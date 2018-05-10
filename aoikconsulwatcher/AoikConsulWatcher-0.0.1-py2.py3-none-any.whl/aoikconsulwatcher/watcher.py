# coding: utf-8
from __future__ import absolute_import

from argparse import ArgumentParser
import sys
from threading import Thread
import time
from traceback import format_exc

from aoikimportutil import import_obj
from consul import Consul


def get_service_infos(consul_obj, update_index):
    update_index, map_service_name_to_tags = consul_obj.catalog.services(
        update_index,
        consistency='consistent'
    )

    # Map service name to info dict
    service_infos = {}

    for service_name, service_tags in map_service_name_to_tags.items():
        _, node_infos = consul_obj.catalog.service(service_name)

        service_infos[service_name] = {
            'tags': service_tags,
            'nodes': node_infos,
        }

    return update_index, service_infos


def watch_services(config_module):
    consul_obj = Consul(
        host=config_module.CONSUL_HOST,
        port=config_module.CONSUL_PORT,
    )

    handle_service_infos = config_module.handle_service_infos

    update_index = None

    while True:
        try:
            update_index, service_infos = get_service_infos(
                consul_obj, update_index
            )
        except Exception:
            msg = 'Failed getting service infos. Sleep 10s before retry.\n'

            sys.stderr.write(msg)

            msg = 'Traceback:\n---\n{0}---\n'.format(format_exc())

            sys.stderr.write(msg)

            time.sleep(10)

            continue

        while True:
            try:
                handle_service_infos(service_infos)

                break
            except Exception:
                msg = (
                    'Failed calling `handle_service_infos`.'
                    ' Sleep 10s before retry.\n'
                )

                sys.stderr.write(msg)

                msg = 'Traceback:\n---\n{0}---\n'.format(format_exc())

                sys.stderr.write(msg)

                time.sleep(10)

                continue


def main(args=None):
    arg_parser = ArgumentParser(prog='aoikconsulwatcher')

    arg_parser.add_argument(
        '-c', '--config',
        dest='config_module_uri',
        default='aoikconsulwatcher.config',
        metavar='URI',
        help='Config module URI. Default is `aoikconsulwatcher.config`.',
    )

    args = arg_parser.parse_args(args)

    config_module_uri = args.config_module_uri

    try:
        config_module = import_obj(
            config_module_uri,
            mod_name='aoikconsulwatcher._config'
        )
    except Exception:
        msg = 'Failed loading config module: {0}\n'.format(config_module_uri)

        sys.stderr.write(msg)

        msg = 'Traceback:\n---\n{0}---\n'.format(format_exc())

        sys.stderr.write(msg)

        return -1

    watch_services_thread = Thread(
        target=watch_services,
        kwargs={'config_module': config_module}
    )

    watch_services_thread.daemon = True

    watch_services_thread.start()

    while True:
        time.sleep(1)
