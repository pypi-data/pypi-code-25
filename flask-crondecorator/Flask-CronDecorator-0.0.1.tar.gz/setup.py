from setuptools import setup, find_packages

__version__ = '0.0.1'

setup(
    name='Flask-CronDecorator',
    version=__version__,
    description='Securely decorates Google Cloud Cron Endpoints via convention and X-Appengine-Cron header',
    url='https://github.com/MobiusWorksLLC/Flask-CronDecorator.git',
    author='Tyson Holub',
    author_email='tholub@mobiusworks.com',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'Flask'
    ]
)
