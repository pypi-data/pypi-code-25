from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    author='Davide Rizzo',
    author_email='sorcio@gmail.com',
    name='randre',
    version='0.1.0',
    description='Generate random text from regular expression patterns',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/sorcio/randre',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3',
    py_modules=["randre"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
