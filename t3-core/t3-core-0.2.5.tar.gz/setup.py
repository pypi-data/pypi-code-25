#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
from setuptools import setup, find_packages
import versioneer

readme_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
try:
    from m2r import parse_from_file
    readme = parse_from_file(readme_file)
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        readme = f.read()

requirements = [
    # Django
    'Django>=2.0',
    'psycopg2',

    # Django Rest Framework
    'djangorestframework>=3.8',
    'django-filter>=1.1',
    'markdown>=2.6',
    'coreapi>=2.3',
    'django-crispy-forms',

    # Django AWS
    'django-storages==1.6.6',
    'boto3==1.7.6',

    # Other
    'requests',

    # Testing
    'coverage',
    'pytest',
    'pytest-cov',
    'pytest-django',

    # Linting
    'pylint',
    'pylint-django',
    'pep8',
    'autopep8',
    'pylama',
    'pylama_pylint',

    # Packaging
    'm2r',
]

setup_requirements = requirements

test_requirements = []

setup(
    author="Travis Krause",
    author_email='travis.krause@t-3.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="Boilerplate to quickly setup a Django Rest Framework Microservice for T3",
    # entry_points={
    #     'console_scripts': [
    #         'manage=manage:main',
    #         'wsgi=wsgi',
    #         'cloaked_forge=cloaked_forge:main',
    #     ],
    # },
    install_requires=requirements,
    # setup_requires=setup_requirements,
    long_description=readme,
    include_package_data=True,
    keywords='t3 t3-python-core',
    name='t3-core',
    packages=find_packages('./src'),
    package_dir={'': 'src'},
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/nwcell/t3_django_microservice',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    # zip_safe=False,
)
