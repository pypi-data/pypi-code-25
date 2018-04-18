import sys

from setuptools import setup, find_packages


with open('VERSION') as version_fp:
    VERSION = version_fp.read().strip()


# This is used only in development of the django-perms package itself.
# The idea is to install the newest version of Django that works with
# the Python version in use. Tox is used to test all supported
# combinations of Python/Django.
py_version = sys.version_info[:2]
if py_version == (2, 7):
    django_spec = 'django>=1.11,<1.12',
if py_version == (3, 3):
    django_spec = 'django>=1.8,<1.9',
else:
    django_spec = 'django>=2.0,<2.1',


setup(
    name='django-perms',
    version=VERSION,
    url='https://github.com/PSU-OIT-ARC/django-perms',
    author='Matt Johnson',
    author_email='mdj2@pdx.edu',
    maintainer='Wyatt Baldwin',
    maintainer_email='wbaldwin@pdx.edu',
    description='Syntactic sugar for handling permission functions in views, templates, and code',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'six>=1.11.0',
    ],
    extras_require={
        'dev': [
            'coverage',
            django_spec,
            'flake8',
            'tox',
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
