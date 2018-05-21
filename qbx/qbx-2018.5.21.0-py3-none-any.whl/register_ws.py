import json
import socket

import requests
from docopt import docopt as docoptinit

register_kong_doc = """
Usage:
    register_ws [options]
    
Options:
    --ot             1Token Endpoint (it will register into  config:v1ws also)
    --name=<name>
    --uri=<uri>
    --ip=<ip>
    --port=<port>
"""


def register_ws(argv):
    docopt = docoptinit(register_kong_doc, argv)
    dst_list = ['wsv2']
    if docopt['--ot']:
        dst_list.append('v1ws')
    for dst in dst_list:
        r = requests.get('http://api.qbtrade.org/redis/get?key=config:{dst}&raw=1')
        r = r.json()
        port = docopt['--port']
        if not docopt['--ip']:
            ip = socket.gethostbyname(socket.gethostname())
        else:
            ip = docopt['--ip']
        uri = docopt['--uri']
        r[docopt['--name']] = f'ws://{ip}:{port}/{uri}'
        print(r)

        data = {'key': f'config:{dst}', 'value': json.dumps(r)}
        r = requests.post('http://api.qbtrade.org/redis/set', data)
        print(r.json())


if __name__ == '__main__':
    # register_kong(['--name', 'pytest', '--ip', '1.2.3.4', '--uris', '/pytest', '--port', '8080'])
    register_ws(['--name', '/pytest', '--uri', '/ws', '--port', '3000'])
