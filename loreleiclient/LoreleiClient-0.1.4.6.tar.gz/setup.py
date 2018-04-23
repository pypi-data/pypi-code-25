from setuptools import setup, find_packages

setup(name='LoreleiClient',
    version='0.1.4.6',
    description='The text based MUD made by Lorinthio',
    author='Lorinthio',
    author_email='benrandallswg@gmail.com',
    packages=find_packages(),
    install_requires=[
        'twisted',
        'pygame',
        'enum34',
        'LoreleiLib'
    ],
    zip_safe=False)