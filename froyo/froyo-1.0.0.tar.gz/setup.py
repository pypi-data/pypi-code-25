

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='froyo',
    version='1.0.0',
    description='Command line tool that prepares a static website for distribution, processing server side includes locally.',
    long_description = long_description,
    url='https://github.com/kartikye/froyo/',
    author='Kartikye Mittal',
    author_email='kartikye.mittal+froyo@gmail.com',
    license='MIT',
    packages=['froyo'],
    zip_safe=False,
    python_requires='>=3',
    install_requires=[
        'css-html-js-minify',
        'Pillow',
        'watchdog'
    ],
    entry_points={  # Optional
        'console_scripts': [
            'froyo=froyo:main',
        ],
    }
)