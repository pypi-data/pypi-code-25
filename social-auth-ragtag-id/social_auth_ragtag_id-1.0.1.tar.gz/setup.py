from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

    setup(
        name='social_auth_ragtag_id',
        version='1.0.1',
        description='An OAuth2 backend for social-auth-core',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/RagtagOpen/python-social-auth-ragtag-id',
        author='Ragtag',
        author_email='opensource@ragtag.org',
        packages=find_packages(exclude=['contrib', 'docs', 'tests']),
        install_requires=['python-social-auth'],
        project_urls={
            'Bug Reports': 'https://github.com/RagtagOpen/python-social-auth-ragtag-id/issues',
            'Source': 'https://github.com/RagtagOpen/python-social-auth-ragtag-id',
        },
        classifiers=[
            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            # Pick your license as you wish
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
        ],
    )
