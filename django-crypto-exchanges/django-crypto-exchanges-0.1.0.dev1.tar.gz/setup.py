#!/usr/bin/env python
import io
from setuptools import setup, find_packages

install_requirements = [
    'gdax==1.0.6',
    'python-binance==0.6.6'
]

test_requirements = []

long_description = io.open('README.md', encoding='utf-8').read()

setup(
    name='django-crypto-exchanges',
    version='0.1.0.dev1',
    author='Haldun Anil',
    author_email='haldunanil@gmail.com',
    license='MIT',
    url='https://github.com/haldunanil/django-crypto-exchanges',
    packages=find_packages(),
    install_requires=install_requirements,
    tests_require=test_requirements,
    description='A Python client for cryptocurrency exchange APIs',
    long_description=long_description,
    download_url='https://github.com/haldunanil/django-crypto-exchanges/archive/master.zip',
    keywords=['orderbook', 'trade', 'bitcoin', 'ethereum', 'BTC', 'ETH', 'client', 'api', 'wrapper', 'exchange', 'crypto', 'currency', 'cryptocurrency', 'trading', 'trading-api', 'coinbase', 'binance', 'gdax', 'gdax-api'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',        
    ],
)