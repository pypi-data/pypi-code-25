
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='opedia',
    version='0.1.4',
    description='Opedia is an open source database service to integrate, visualize, and analyze ocean datasets such as satellite data, in-situ observations, and model outputs.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mdashkezari/opedia',
    author='Mohammad D. Ashkezari',
    author_email='demo.80@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='ocean oceanography database dataset satellite model in-situ remote sensing machine learning data visualization',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    #install_requires=['matplotlib', 'numpy', 'pandas', 'scipy', 'bokeh', 'pyodbc', 'dropbox'],
)
