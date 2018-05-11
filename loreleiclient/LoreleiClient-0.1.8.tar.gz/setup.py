from setuptools import setup, find_packages

# http://rst.ninjs.org for rst parsing

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='LoreleiClient',
    version='0.1.8', # Don't forget to make a changelog entry in README.rst
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
    url='https://pypi.org/project/LoreleiClient/',
    zip_safe=False)