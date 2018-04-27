from setuptools import setup

import os
from itertools import chain

def find_files(relpath):
    prefix = os.path.join(os.path.dirname(__file__), 'probe')
    for dirname, _, files in os.walk(os.path.join(prefix, relpath)):
        for filename in files:
            yield os.path.join(dirname, filename)[len(prefix) + 1:]

setup(
    name='probe-lib',
    version='0.1',
    description='Beep? Boop? Beepboop!',
    author='Philipp Benjamin Koeppchen',
    author_email='info@triplet-gmbh.de',
    url='https://triplet-gmbh.de/',
    packages=[
        'probe'
    ],
    package_data={
        '': list(chain(
                find_files('static'),
                find_files('migrations'),
                find_files('templates'),
        ))
    },
    install_requires=[
        'Flask==0.12.2',
        'requests>=2.18.1',
        'sqlalchemy>=1.2.5',
        'alembic==0.9.9',
    ],
)
