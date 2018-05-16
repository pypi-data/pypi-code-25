from codecs import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aerovane',
    version='0.2.4',
    packages=find_packages(),
    description='Simple weather report in the terminal',
    long_description=long_description,
    url='https://github.com/dfundingsland/aerovane',
    author='David Fundingsland',
    author_email='david@fundings.land',
    license='MIT',
    download_url='https://github.com/dfundingsland/aerovane/master.zip',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    install_requires=[
        'requests >= 2.18.4',
        'click >= 6.7',
        'huepy >= 0.9.8.1',
        'pyowm >= 2.8.0'

    ],
    entry_points='''
        [console_scripts]
        aerovane=aerovane.cli:cli
    ''',
    python_requires='>=3.4'
)
