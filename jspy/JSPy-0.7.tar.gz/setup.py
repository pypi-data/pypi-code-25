from setuptools import setup
import io

with io.open('README.md', encoding='utf-8') as readme:
	long_description = readme.read()

setup(name='JSPy',
      description='Python Library that runs Javascript',
      version='0.7',
      long_description=long_description,
      long_description_content_type='text/markdown',
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
