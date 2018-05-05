# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['apistar_ponyorm']

package_data = \
{'': ['*']}

install_requires = \
['apistar>=0.5.0.0', 'pony>=0.7.0.0']

setup_kwargs = {
    'name': 'apistar-ponyorm',
    'version': '0.2.12',
    'description': 'Third-party for apistar using pony orm',
    'long_description': 'apistar-ponyorm\n###########################\n\n.. image:: https://travis-ci.org/jgirardet/apistar-ponyorm.svg?branch=master\n    :target: https://travis-ci.org/jgirardet/apistar_ponyorm\n.. image:: https://coveralls.io/repos/github/jgirardet/apistar-ponyorm/badge.svg\n   :target: https://coveralls.io/github/jgirardet/apistar_ponyorm\n.. image:: https://badge.fury.io/py/apistar-ponyorm.svg\n   :target: https://pypi.python.org/pypi/apistar_ponyorm/\n   :alt: Pypi package\n\n\n**Third-party for apistar using pony orm**\n\n* License : GNU General Public License v3 \n* Documentation: https://apistar_ponyorm.readthedocs.org/en/latest/\n* Source: https://github.com/jgirardet/apistar-ponyorm\n\nFeatures\n**********\n\n- Apistar Hook : PonyDBSession which give auto apply db_session to views.\n\n\nUsage\n********\n\nThis should be added in App declaration :\n\napp = App(routes=[route], event_hooks=[PonyDBSession()])\n\n.. code-block:: python\n    \n    # main app.py file\n    from apistar_ponyorm import PonyDBSession\n    # ...\n    app = App(routes=[route], event_hooks=[PonyDBSession()])\n\n\n    # myviews.py\n    from myproject import db # PonyORM Database Instance\n\n    def myviews():\n      retun db.MyEntity.to_dict()\n\n    # No need to add @db_session\n\n\nChangelog\n**********\n\n0.2.10 :\n  - use poetry\n0.2.0 : \n  - add PonyDBSession',
    'author': 'Jimmy Girardet',
    'author_email': 'ijkl@netc.fr',
    'url': 'https://github.com/jgirardet/apistar_ponyorm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>= 3.5.0.0, < 4.0.0.0',
}


setup(**setup_kwargs)
