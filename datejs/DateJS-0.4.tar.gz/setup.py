from setuptools import setup

long_description = open("README.rst", "r").read() 

setup(name='DateJS',
      description='Python Library that converts Javascript Date objects to Python Datetime objects',
      version='0.4',
      long_description=long_description,
      url='https://github.com/rithik/DateJS',
      author='Rithik Yelisetty',
      author_email='rithik@gmail.com',
      license='MIT',
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3'
      ],
      packages=['DateJS'],
      install_requires=[
          'JSPy>=1.0.0',
          'pytz>=2016.10'
      ],
      entry_points={
          'console_scripts': [
              'DateJS=DateJS.main:run'
          ]
      }
)
