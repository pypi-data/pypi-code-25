#!/usr/bin/python3
"""Setup script for django_pain."""
from setuptools import find_packages, setup

import django_pain

INSTALL_REQUIRES = ['Django>=2.0', 'django-money']
EXTRAS_REQUIRE = {'quality': ['isort', 'flake8', 'pydocstyle', 'polint']}

setup(name='django-pain',
      version=django_pain.__version__,
      description='Django application for managing bank payments and invoices',
      url='https://github.com/stinovlas/django-pain',
      author='Jan Musílek',
      author_email='jan.musilek@nic.cz',
      packages=find_packages(),
      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ])
