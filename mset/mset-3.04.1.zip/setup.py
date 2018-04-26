
from setuptools import find_packages, setup
from codecs import open

setup(
    name='mset',
    author='Marmoset LLC',
    author_email='support@marmoset.co',
		version="3.04.1",
    license='MIT',
    keywords=['mset', 'marmoset', 'toolbag', 'hexels'],
    download_url='https://marmoset.co/toolbag/',
    description='A no-op version of the runtime python library included in Marmoset Toolbag.',
    url='https://marmoset.co',
    classifiers=[
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    platforms='ANY',
    packages=find_packages(),
    long_description=open("README.rst").read()
)


