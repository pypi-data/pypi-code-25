from setuptools import setup
import pathlib

from mountapi import version


package_info = {
    'name': version.__name__,
    'version': version.__version__,
    'description': version.__description__,
    'author': version.__author__,
    'author_email': version.__author_email__,
    'url': version.__url__,
    'license': version.__license__,
}

with open('README.rst', 'r') as f:
    readme = f.read()


def get_packages(path):
    return [str(x) for x in path.glob('**') if (x / '__init__.py').exists()]


setup(
    name=package_info['name'],
    version=package_info['version'],
    description=package_info['description'],
    long_description=readme,
    author=package_info['author'],
    author_email=package_info['author_email'],
    url=package_info['url'],
    packages=get_packages(pathlib.Path('mountapi')),
    license=package_info['license'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3.6',
    ],
)
