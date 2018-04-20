from setuptools import setup

setup(
     name='csc440-user-database',    # This is the name of your PyPI-package.
     version='0.1',                          # Update the version number for new releases
     scripts=['user', 'test_user']                  # The name of your scipt, and also the command you'll be using for calling it
)