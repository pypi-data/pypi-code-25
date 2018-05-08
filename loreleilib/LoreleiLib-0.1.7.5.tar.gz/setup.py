from setuptools import setup, find_packages


setup(name='LoreleiLib',
    version='0.1.7.5', # Don't forget to make a changelog entry in README.rst
    description='The text based MUD made by Lorinthio',
    author='Lorinthio',
    author_email='benrandallswg@gmail.com',
    packages=find_packages(),
    install_requires=[
      'twisted',
      'pygame',
      'enum34'
    ],
    zip_safe=False)