"""A setuptools based setup module.
"""

from setuptools import setup, find_packages

def read_description():
    try:
        return open('README.md').read()
    except FileNotFoundError:
        return open('lib/python/README.md').read()

setup(
    name='ridi-cms-sdk',
    packages=[
        'ridi.cms',
        'ridi.cms.thrift.AdminAuth',
        'ridi.cms.thrift.AdminMenu',
        'ridi.cms.thrift.AdminTag',
        'ridi.cms.thrift.AdminUser',
        'ridi.cms.thrift.Errors',
    ],
    version='2.3.2-rc.1',
    description='Ridi CMS SDK',
    long_description=read_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/ridi/cms-sdk',
    keywords=['cmssdk', 'ridi', 'ridibooks'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'thrift>=0.10.0',
        'requests>=2.0.0',
    ],
)
