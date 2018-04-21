from setuptools import setup, find_packages
from pay_api import VERSION

setup(
    name = 'intgr-pay-api',
    version = VERSION.replace(' ', '-'),
    description = 'An API for PayU allowing to integrate online payments using PayU.',
    author = 'Integree Business Solutions',
    author_email = 'dev@integree.eu',
    url = 'https://github.com/integree/intgr-payu-api',
    download_url = 'https://pypi.python.org/packages/source/i/intgr-payu-api/intgr-payu-api-%s.zip' % VERSION,
    keywords = 'api pay payments online utils integree',
    packages = find_packages(),
    include_package_data = True,
    license = 'MIT License',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires = [
        'django-appconf',
        'requests',
        'babel',
        'money',
        'paypalrestsdk==1.13.1',
    ],
    zip_safe = False)
