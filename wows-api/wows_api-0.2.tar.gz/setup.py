import re
from setuptools import setup

with open('wows_api/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='wows_api',
    version=version,
    packages=['wows_api'],
    install_requires=['requests'],
    url='https://github.com/pachkun/wows_api',
    author='pachkun',
    author_email='pachkunishka@gmail.com',
    description='Работа с api world of warship',
    python_requires='>=3.6',
    include_package_data=True
)
