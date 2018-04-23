import os

from setuptools import setup

from logs import __version__

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

install_requires = [
    'pymongo>=3.6.1',
    'django>=2.0.4'
]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-logs-middleware',
    version=__version__,
    packages=['logs'],
    include_package_data=True,
    license='MIT License',
    description='Logs registry for services',
    long_description=README,
    author='Angel Alfaro',
    author_email='a3herrera@gmail.com',
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
