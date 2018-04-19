from setuptools import setup

setup(
    name = 'http_request_aggregator',
    packages = ['http_request_aggregator'],
    version = '0.3',
    description = 'Collect multiple http requests asynchronously',
    install_requires = [
    'tornado',
    ],
    url = 'https://github.com/ajmunton/http_request_aggregator',
    download_url = 'https://github.com/ajmunton/http_request_aggregator/archive/0.3.tar.gz',
    author = 'Adam Munton',
    author_email='a.j.munton@gmail.com',
)