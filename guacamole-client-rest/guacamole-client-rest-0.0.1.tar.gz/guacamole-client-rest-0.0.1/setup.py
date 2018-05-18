from setuptools import find_packages, setup


setup(
    name='guacamole-client-rest',
    version='0.0.1',
    description='Python REST API client for Guacamole 0.9.13 version',
    author='feifeixj',
    author_email='15851862881@163.com',
    url='https://github.com/feifeixj/guacamole-client-rest-pyhton',
    packages=find_packages(),
    install_requires=['requests'],
)
