from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
        name='shakespeare-insult',
        version='1.0.2',
        description='Generate insults in the style of Bill Shakespeare',
        long_description=long_description,
        long_description_content_type='text/markdown',
        author='Derek Morey',
        author_email='derek.o.morey@gmail.com',
        license='GPL-3.0',
        url='https://github.com/Oisota/shakespeare-insult',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: OS Independent',
            ],
        keywords=['William Shakespeare', 'Shakespeare', 'insult'],
        py_modules=['bill']
        )
