# coding: utf-8
from __future__ import absolute_import

import os


CONSUL_HOST = os.environ.get('CONSUL_HOST', '127.0.0.1')

CONSUL_PORT = int(os.environ.get('CONSUL_PORT', '8500'))


def handle_service_infos(service_infos):
    for service_name, service_info in service_infos.items():
        print('\nService name: {0}'.format(service_name))

        tags = service_info['tags']

        if tags:
            print('Service tags: {0}'.format(' '.join(tags)))

        for node in service_info['nodes']:
            print('{0}:{1}'.format(
                node['ServiceAddress'], node['ServicePort'])
            )
