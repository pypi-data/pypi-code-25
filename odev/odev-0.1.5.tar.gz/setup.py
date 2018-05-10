import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '0.1.5'

setup(
    name='odev',
    version=version,
    description="odev",
    long_description=README,
    classifiers=[
    ],
    keywords='odev',
    author='me',
    author_email='me@example.org',
    url='https://example.org',
    license='LGPL v3',
    py_modules=['odev'],
    include_package_data=True,
    install_requires=[
        'future',
    ],
    entry_points='''
    ''',
)
