from distutils.core import setup
import os


def readme():
    path = os.path.sep.join([
        os.path.abspath(os.path.dirname(__file__)),
        'README.md'
    ])
    with open(path) as f:
        return f.read()


setup(
    name='zaach',
    version='1.0.3',
    packages=['zaach',],
    author="Fabian Topfstedt",
    url="https://bitbucket.org/fabian/zaach",
    license='The MIT Licence',
    long_description=readme(),
    keywords = ['base64url', 'timezone', 'conversion'],
    classifiers = [],
)
