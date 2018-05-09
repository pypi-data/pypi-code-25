from setuptools import setup, find_packages

setup(
    name='aws-event-parser',
    version='0.3.1',
    packages=find_packages(),
    author='Md Mehrab Alam',
    author_email='mdmehrab.alam@delhivery.com',
    long_description=open('README.md').read(),
    url='https://bitbucket.org',
    description='Small wrapper to aws event and return data',
    install_requires=['boto3'],
    test_suite='test',
)
