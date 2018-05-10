from setuptools import setup

setup(
    name='gamecredits',
    version='0.1.3',
    description='Tools for working with the GameCredits cryptocurrency',
    url='https://github.com/gamecredits-project/python-gamecredits',
    download_url='https://github.com/gamecredits-project/python-gamecredits/archive/0.1.3.tar.gz',
    author='Nikola Divic',
    author_email='divicnikola@gmail.com',
    license='MIT',
    packages=['gamecredits'],
    zip_safe=False,
    install_requires=[
        'pybitcointools',
        'simplejson',
        'python-bitcoinrpc'
    ],
    keywords=['gamecredits', 'cryptocurrency', 'bitcoin'],
    classifiers=[]
)
