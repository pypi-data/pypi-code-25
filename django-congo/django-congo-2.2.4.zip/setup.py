# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from congo import VERSION

setup(
    name = 'django-congo',
    version = VERSION.replace(' ', '-'),
    description = 'Congo contains many useful tools for faster and more efficient Django application developing.',
    author = 'Integree Bussines Solutions',
    author_email = 'dev@integree.eu',
    url = 'https://github.com/integree/django-congo',
    download_url = 'https://pypi.python.org/packages/source/d/django-congo/django-congo-%s.zip' % VERSION,
    keywords = 'django-congo congo django utils integree',
    packages = find_packages(),
    include_package_data = True,
    license = 'MIT License',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django :: 1.10',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires = [
        'django_user_agents',
        'django-appconf',
        'django-mptt==0.9',
        'django-parler==1.9',
        'pillow',
        'urllib3==1.22',
        'premailer',
        'pycrypto',
        'py-moneyed',
        'suds',
        'unidecode',
    ],
    zip_safe = False)
