from setuptools import setup, find_packages

setup(
    name='DigitalSystems',
    version='0.0.1',
    author='Shivam Patel',
    author_email='16bce081@nirmauni.ac.in',
    url='http://pypi.python.org/pypi/DigitalSystems/',
    # license=open('docs/LICENSE.txt').read(),
    description='An attempt to create a python library for digital systems which could be used for further advanced studies.',
    # long_description=open('README.md').read(),
    install_requires=["networkx >= 1.8.1", "bitstring >= 3.1.3"],
    keywords = ['digital','systems','binary','research','shivam','patel'],
    #package_data={'data': ['README.md']},
    #include_package_data=True,
)
