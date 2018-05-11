from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='jc-pytools',
    version='1.0.1',
    description='Simple everyday Python tools.',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jadon Calvert',
    author_email='calvertjadon@gmail.com',
    url='https://bitbucket.org/calvertjadon/jcpytools/',
    packages=['jctools'],
)
