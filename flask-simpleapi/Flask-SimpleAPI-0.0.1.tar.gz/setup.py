"""
Flask-SimpleAPI
-------------

Very simple way to create an API with Flask and MongoDB:
- simple route
- auto detect and render json if dict, list or MongoEngine object
"""
from setuptools import setup, find_packages
packages = find_packages()

setup(
    name='Flask-SimpleAPI',
    version='0.0.1',
    url='http://hthieu.xyz',
    license='MIT',
    author='Bkinno',
    author_email='tronghieu.ha@gmail.com',
    description='Very simple way to create an API with Flask',
    long_description=__doc__,
    # py_modules=['flask_simple_api'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'flask',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
