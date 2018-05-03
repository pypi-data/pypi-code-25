# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['apistar_ponyorm']

package_data = \
{'': ['*']}

install_requires = \
['apistar>=0.5.10.0,<0.6.0.0', 'pony>=0.7.3.0,<0.8.0.0']

setup_kwargs = {
    'name': 'apistar-ponyorm',
    'version': '0.2.9',
    'description': '',
    'long_description': None,
    'author': 'jgirardet',
    'author_email': 'ijkl@netc.fr',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>= 3.5.0.0, < 4.0.0.0',
}


setup(**setup_kwargs)
