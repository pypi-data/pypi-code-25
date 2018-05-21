from setuptools import setup, find_packages

setup(
    name='nameko-redisy',
    version='1.0.2',
    url='https://github.com/qileroro/nameko-redisy/',
    license='Apache License, Version 2.0',
    author='qileroro',
    author_email='qileroro@qq.com',
    packages=find_packages(),
    install_requires=[
        "nameko>=2.0.0",
        "redis",
    ],
    description='Redis dependency for nameko services',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)