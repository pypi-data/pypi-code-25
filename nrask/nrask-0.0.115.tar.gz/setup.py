from setuptools import find_packages,setup

setup(
    description='Viking Makt Framework',
    install_requires=[
        'pika',
        'tornado',
        'simplejson',
        'colorlog',
        'bencode',
    ],
    license='https://bitbucket.org/habboi/nrask/raw/master/LICENSE',
    maintainer='Guilherme Nemeth',
    maintainer_email='guilherme.nemeth@gmail.com',
    name='nrask',
    packages=find_packages(),
    url='https://bitbucket.org/habboi/nrask',
    version="0.0.115"
)
