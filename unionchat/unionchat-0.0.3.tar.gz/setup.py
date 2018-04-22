from setuptools import setup

setup(
    name='unionchat',
    version='0.0.3',
    packages=['unionchat'],
    url='https://github.com/GeoffreyWesthoff/union.py',
    license='MIT',
    author='Geoffrey Westhoff',
    author_email='geoffreywesthoff@gmail.com',
    description='Union chat API wrapper',
    install_requires=['websockets', 'pyee']
)
