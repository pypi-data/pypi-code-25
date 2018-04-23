from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mindstrong',
    version='1.0',
    description='Mindstrong Digital Biomarker Model Fitting',
    long_description=long_description,
    url='http://mindstronghealth.com',
    author='Mindstrong Health Data Science',
    author_email='datascience@mindstronghealth.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3',
    ],
    keywords='digital biomarkers, supervised kernel PCA, machine learning, cross-validation',
    packages=['mindstrong'],
    install_requires=['scipy','numpy','pandas','sklearn'],
    package_data={'mindstrong':'mindstrong/data/example_features.csv', 'mindstrong':'mindstrong/data/example_targets.csv'},
    include_package_data=True,
    scripts = ['example.py'],
)
