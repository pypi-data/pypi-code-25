from setuptools import setup,find_packages
from codecs import open
from os import path

path= path.abspath(path.dirname(__file__))



setup(
     name='Pongola_Email_Batch',
     version='0.1',
    description='this application sends Emails to growers about grower Report',
    scripts=['BatchFile.py'],
    Classifiers=[ 'Development Status :: 3 - Alpha','Intended Audience :: Growers','Programming Language :: Python :: 2.7'],
    packages= find_packages(exclude=['contrib', 'docs', 'tests'])

)
