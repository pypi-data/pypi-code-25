from setuptools import setup
setup(
    name = 'clogging',
    packages = ['clogging'],
    version = '0.1',
    install_requires = ['PyYAML>=3.12'],
    description = 'Configurable Logging Boilerplate for the Autologging Module',
    long_description = open('README.rst').read(),
    author = 'Ryan Miller',
    author_email = 'ryan@devopsmachine.com',
    license = 'MIT',
    url = 'https://github.com/RyanMillerC/clogging',
    download_url = 'https://github.com/RyanMillerC/clogging/archive/0.1.tar.gz',
    keywords = ['logging', 'yaml', 'autologging'],
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Logging'
    ]
)
