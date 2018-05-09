"""
modernremodel
----------------

Very simple yet powerful and extensible Object Document Mapper for RethinkDB, written in Python.

"""

from setuptools import setup, find_packages


setup(
    name='modernremodel',
    version='0.5.1',
    url='https://github.com/seandavidmcgee/modernremodel',
    license='MIT',
    author='Sean McGee',
    author_email='sean@iluminere.com',
    description='Modern RethinkDB ODM',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'rethinkdb',
        'inflection',
        'six'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
