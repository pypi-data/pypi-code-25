from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django_abc',
    version='1.0.0',
    description='extension to django inheritance for automatically casting base to appropriate subclass',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ebrush/django_abc',
    author='Samuel Brush',
    author_email='s.e.brush1@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='django decorators inheritance',
    packages=find_packages(include=['django_abc']),
    project_urls={
        'Bug Reports': 'https://github.com/ebrush/django_abc/issues',
        'Source': 'https://github.com/ebrush/django_abc',
    },
)
