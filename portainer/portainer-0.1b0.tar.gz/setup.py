from setuptools import setup

setup(
    name='portainer',
    packages=['portainer'],
    version='0.1-beta',
    description='Python module to interact with the Portainer API',
    author='Renato Covarrubias',
    author_email='rnt@rnt.cl',
    url='https://github.com/rnt/python-portainer',
    download_url='https://github.com/rnt/python-portainer/archive/0.1.tar.gz',
    install_requires=[
        'requests',
    ],
    keywords=['portainer'],
    classifiers=[],
)
