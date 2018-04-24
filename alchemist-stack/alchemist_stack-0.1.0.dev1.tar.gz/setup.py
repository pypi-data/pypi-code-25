from setuptools import setup, find_packages
from codecs import open
from os import path

root = path.abspath(path.dirname(__file__))

with open(path.join(root, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Application Name:
    name='alchemist_stack',

    # Version Number:
    version='0.1.0.dev1',

    # Classifiers
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],

    # Keywords
    keywords='sqlalchemy databases',

    # Application Author Details:
    author='H.D. "Chip" McCullough IV',
    author_email='hdmccullough.work@gmail.com',

    # Packages:
    packages=find_packages(exclude=['models', 'repos', 'tables', 'tests']),

    # Details:
    url='https://github.com/mcculloh213/alchemist-stack',
    project_urls={
        'Documentation': 'https://github.com/mcculloh213/alchemist-stack',
        #'Funding': 'https://github.com/mcculloh213/alchemist-stack',
        'Source': 'https://github.com/mcculloh213/alchemist-stack',
        'Issue Tracker': 'https://github.com/mcculloh213/alchemist-stack/issues'
    },
    license='MIT',
    description='A Thread-Safe, Multi-Session/Multi-Connection Model-Repository-Context base for SQL Alchemy',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # Dependent Packages (Distributions):
    install_requires=[
        'sqlalchemy',
    ],

    # Requires Python Version:
    python_requires='>=3'
)