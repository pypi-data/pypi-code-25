from distutils.core import setup

setup(
    name='bchmemo',
    version='0.0.3.1',
    packages=['bchmemo','bchmemo.bitcash_modified'],
    url='https://github.com/remem9527/bchmemo',
    license='MIT',
    author='remem9527',
    author_email='wszd163@163.com',
    description='A python package for memo. Memo is an on-chain social network built on Bitcoin Cash',
    long_description=open('README.rst', 'r').read(),
    keywords=[
        'bitcoincash',
        'social network',
        'memo',
        'on-chain data',
        'OP_RETURN',
    ],

    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],

    install_requires=['bitcash']

)
