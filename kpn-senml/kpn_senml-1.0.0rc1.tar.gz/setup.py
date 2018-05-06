from setuptools import setup

setup(
    name='kpn_senml',
    version='1.0.0rc1',
    packages=['kpn_senml'],
    url='https://github.com/jan-bogaerts/slate',
    license='APACHE',
    author='Jan Bogaerts',
    author_email='jb@elastetic.com',
    description='generate and parse senml json and cbor data',
    keywords='senml kpn cbor json',
    install_requires=[
          'cbor2',
    ]
)
