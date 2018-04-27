"""
store_beat
-------------

This is the description for that library
"""
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='store_beat',
    version='2018.04.02',
    url='https://github.com/pingf/store_beat.git',
    license='BSD',
    author='Jesse MENG',
    author_email='pingf0@gmail.com',
    description='beat with store',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    py_modules=['store_beat'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    packages=['store_beat', 'store_beat.dist'],
    zip_safe=False,
    package_data={
        'store_beat.dist': ['*', 'static/js/*', 'static/css/*']
    },
    include_package_data=True,
    platforms='any',
    install_requires=[
        'aiohttp', 'wrap', 'store', 'celery', 'redis'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
