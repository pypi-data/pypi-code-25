from os import path
from setuptools import find_packages, setup

VERSION = "0.9.1"
DESCRIPTION = "BBGLab web framework"


# Get requirements from the requirements.txt file
directory = path.dirname(path.abspath(__file__))
with open(path.join(directory, 'requirements.txt')) as f:
    required = f.read().splitlines()

# Get the long description from the README file
with open(path.join(directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="bgweb",
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url="https://bitbucket.org/bgframework/bgweb",
    author="Barcelona Biomedical Genomics Lab",
    author_email="bbglab@irbbarcelona.org",
    package_data={'bgweb': ['*.conf.template', '*.confspec']},
    packages=find_packages(),
    install_requires=required,
    project_urls={'BBGLab website': 'https://bbglab.irbbarcelona.org'},
)
