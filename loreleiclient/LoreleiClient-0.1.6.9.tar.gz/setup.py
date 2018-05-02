from setuptools import setup, find_packages

long_description = ""

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='LoreleiClient',
    version='0.1.6.9', # Don't forget to make a changelog entry in README.rst
    description='The text based MUD made by Lorinthio',
    author='Lorinthio',
    author_email='benrandallswg@gmail.com',
    long_description=readme(),
    packages=find_packages(),
    install_requires=[
        'twisted',
        'pygame',
        'enum34',
        'LoreleiLib'
    ],
    include_package_data = True,
    package_data = {
    '' : ['*.png'],
    },
    zip_safe=False)