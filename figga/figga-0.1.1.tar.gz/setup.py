# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['figga']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'figga',
    'version': '0.1.1',
    'description': 'A simple configuration manager for Python.',
    'long_description': "# figga\n\nA very simple configuration manager for Python.\n\n[![Travis CI build](https://www.travis-ci.org/berislavlopac/figga.svg?branch=master)](https://www.travis-ci.org/berislavlopac/figga)\n\n\n## Usage\n\n`figga` currently supports three ways of specifying the configuration:\n\n* standard Python dictionary\n* environment variables with a common prefix\n* one or more `INI` files\n\n\n### Basic Usage\n\nThe default mechanism of instantiating a `figga.Configuration` instance is passing a simple Python dictionary:\n\n    from figga import Configuration\n\n    config = Configuration({'foo': 'bar', 'var1': 123, 'VAR2': 'buzz'})\n\nThis mechanism can be easily used to store configuration in any file format which can easily be converted to a `dict`, such as JSON or YAML:\n\n    import json\n    from figga import Configuration\n\n    with open('config.json') as json_config:\n        config = Configuration(json.load(json_config))\n\nThe instantiated object can be used from elsewhere in your code, e.g. if the above instantiation happened in module `somewhere.py`:\n\n    from somewhere import config\n\n    print(config.some_value)\n\nNote that all variable names are normalised to lowercase, and access is case insensitive: `config.foo`, `config.FOO` or `config.Foo` all point to the same value.\n\nIn addition to direct access, values can be retrieved using the `get` method:\n\n    config.get('some_value')\n\nNote that `get` also accepts the `default` argument, the value of which will override the default value specified at instantiation (see below).\n\n\n### Default Values\n\nAll constructor methods accept the argument `default`, which defines the behaviour when a non-existing value is accessed. This argument can handle three different types of default values:\n\n* any object or scalar value, which will be returned as-is\n* a callable, which will be called passing the accessed variable name as the only argument, returning its result\n* a `BaseException` subclass, which will be raised instead of returning a value\n\nIf no default value is specified, an unknown variable will have the value of `None`.\n\n\n### From Environment Variables\n\nAnother option to initialize the configuration manager is by taking the values of all the environment variables which begin with a common prefix:\n\n    import os\n    from figga import Configuration\n\n    os.environ['YOURAPP_VARIABLE'] = 'foo bar'\n\n    config = Configuration.from_environ(prefix='YOURAPP_')\n\n    print(config.yourapp_variable)\n\nOptionally you can remove the prefix from the final configuration variables:\n\n    config = Configuration.from_environ(prefix='YOURAPP_', remove_prefix=True)\n\n    print(config.variable)\n\n\n### From INI Files\n\nAlternatively, `figga.Configuration` can be instantiated using one or more [configparser](https://docs.python.org/3/library/configparser.html)-compatible files:\n\n    from figga import Configuration\n\n    config = Configuration.from_files('config1.ini', '/vars/config2.ini')\n\nIf the file paths are not absolute, they are assumed to be relative to the current working directory. Paths can be either strings or `os.PathLike` instances.\n",
    'author': 'Berislav Lopac',
    'author_email': 'berislav@lopac.net',
    'url': 'https://github.com/berislavlopac/figga',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>= 3.6.0.0, < 4.0.0.0',
}


setup(**setup_kwargs)
