#!/usr/bin/python
import os
import sys
import shutil
from setuptools import setup
from django_rest_swagger_docstring import __version__ as VERSION

if sys.argv[-1] == 'publish':
    if os.system("wheel version"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()
    if os.system("pip freeze | grep twine"):
        print("twine not installed.\nUse `pip install twine`.\nExiting.")
        sys.exit()
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload -r pypi dist/*")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    print("  git push --tags")
    shutil.rmtree('dist')
    shutil.rmtree('build')
    shutil.rmtree('django_rest_swagger.egg-info')
    sys.exit()

README = """
Django REST Swagger docstrings
Supports docstrings in Django Rest Swagger for versions >2.0
Installation
From pip:
pip install django-rest-swagger-docstring
Project @ https://github.com/johniak/django-rest-swagger-docstring
Docs @ https://django-rest-swagger-docstring.readthedocs.io/
"""

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-rest-swagger-docstring-ext',
    version=VERSION,
    install_requires=[
        'coreapi>=2.0.8',
        'openapi-codec>=1.1.7',
        'djangorestframework>=3.5.1',
        'django-rest-swagger>=2.0.0'
    ],
    packages=['django_rest_swagger_docstring'],
    include_package_data=True,
    license='MIT License',
    description='Supports docstrings in Django Rest Swagger for versions >2.0 (extended version)',
    long_description=README,
    test_suite='tests',
    author='HoverHell',
    author_email='hoverhell@gmail.com',
    url='https://github.com/HoverHell/django-rest-swagger-docstring',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
