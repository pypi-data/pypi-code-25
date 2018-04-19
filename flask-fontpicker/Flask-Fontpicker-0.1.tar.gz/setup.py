"""
Flask-Fontpicker
-------------

A Flask extension to add Jquery-UI javascript web font-picker into the template,
it makes adding and configuring multiple font pickers at a time much easier
and less time consuming

How-to: https://github.com/mrf345/flask_fontpicker/
"""
from setuptools import setup


setup(
    name='Flask-Fontpicker',
    version='0.1',
    url='https://github.com/mrf345/flask_fontpicker/',
    download_url='https://github.com/mrf345/flask_fontpicker/archive/0.1.tar.gz',
    license='MIT',
    author='Mohamed Feddad',
    author_email='mrf345@gmail.com',
    description='web font picker flask extension',
    long_description=__doc__,
    py_modules=['fontpicker'],
    packages=['flask_fontpicker'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Flask-Bootstrap'
    ],
    keywords=['flask', 'extension', 'web', 'google', 'font', 'picker', 'Jquery-UI',
              'fontpicker'],
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
