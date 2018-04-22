from setuptools import setup

setup(
    name='flask-fast-cache',    # This is the name of your PyPI-package.
    version='0.0.1.dev1',                          # Update the version number for new releases
    # The name of your scipt, and also the command you'll be using for calling it
    packages=['flask_fast_cache'],
    python_requires='>=3.6',
    author='Ryan Bonham',
    author_email='ryan@transparent-tech.com',
    license='MIT',
    description='Extends',
    url='https://github.com/TransparentTechnologies/pyJSONA',
    install_requires=[
        'Flask>=0.12.0'
    ],
    extras_require={
        'Redis':  ["redis>=2.10.0"]
    }
)
