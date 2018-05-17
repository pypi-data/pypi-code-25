from setuptools import setup

import pypandoc
long_description = pypandoc.convert('README.md', 'rst')

setup(name='JSPy',
      description='Python Library that runs Javascript',
      version='0.9',
      long_description=long_description,
      url='https://github.com/rithik/JSPy',
      author='Rithik Yelisetty',
      author_email='rithik@gmail.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
      ],
      packages=['JSPy'],
      install_requires=[
      ],
      entry_points={
          'console_scripts': [
              'JSPy=JSPy.main:run'
          ]
      }
)
