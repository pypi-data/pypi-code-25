from setuptools import setup, find_packages

long_description = ""

with open('README.txt') as file:
    long_description += file.read()
with open('CHANGELOG.txt') as file:
    long_description += file.read()

setup(name='LoreleiClient',
    version='0.1.6.8', # Don't forget to make a changelog entry in README.txt
    description='The text based MUD made by Lorinthio',
    author='Lorinthio',
    author_email='benrandallswg@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
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