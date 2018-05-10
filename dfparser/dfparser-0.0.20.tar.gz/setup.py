"""Dataforge parser setup script."""
from setuptools import find_packages, setup


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setup(
    name='dfparser',
    packages=find_packages(),
    version='0.0.20',
    description='Parser for dataforge-envelope (http://npm.mipt.ru/'
    'dataforge/) format.',
    author='Vasilii Chernov',
    author_email='kapot65@gmail.com',
    platforms='any',
    url='https://github.com/kapot65/python-df-parser',
    keywords=['dataforge', 'parser'],
    install_requires=parse_requirements("dfparser/requirements.txt"),
    include_package_data=True,
    package_data={
        '': ['*.proto'],
    },
    classifiers=[],
)
