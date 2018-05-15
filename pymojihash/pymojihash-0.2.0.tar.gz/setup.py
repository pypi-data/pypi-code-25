from setuptools import setup
import ast


setup(
    name='pymojihash',
    version='0.2.0',
    include_package_data=True,
    description='Python 3 package for hashing strings to emojis.',
    long_description='hash to emoji',
    author='Lily FYI',
    author_email='hello@lily.fyi',
    packages=['pymojihash',],
    package_dir={'pymojihash': 'pymojihash',},
)
