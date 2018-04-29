from distutils.core import setup
from setuptools import find_packages

requirements = [
    'Django>=1.11.3,<2',
    # Require Postgres -- can't use sqlite because some models use
    # django.contrib.postgres.fields.ArrayField
    'psycopg2==2.7.1',
    'pybomojo==0.1.1',
    'python-slugify>=1.2.4,<2',
]

test_requirements = [
    # Used in test settings
    'dj-database-url==0.4.2',

    # Libraries used by the tests themselves
    'freezegun==0.3.10',
    'mock==2.0.0',

    # Libraries used to discover/run the tests
    'pytest==3.2.0',
    'pytest-django==3.1.2',
]

setup(
    name='bomojo',
    packages=find_packages(),
    version='0.4.0',
    description='Django app for getting movie box office data',
    install_requires=requirements,
    tests_require=test_requirements,
    extras_require={
        'test': test_requirements
    },
    author='Dan Tao',
    author_email='daniel.tao@gmail.com',
    url='https://bitbucket.org/dtao/pybomojo',
    keywords=[],
    classifiers=[],
)
