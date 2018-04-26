import io
import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

with io.open(os.path.join(here, 'VERSION')) as f:
    version = f.read()

setup(name='kinemathic',
      version=version,
      install_requires=[
          "docopt",
          "matplotlib",
          "pandas",
          "seaborn"
      ],
      include_package_data=True,
      scripts=['bin/kine','bin/kine.bat'],
      description='Tool to generate kinematic displays',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='http://github.com/dionresearch/kinemathic',
      author='Francois Dion',
      author_email='fdion@dionresearch.com',
      license='MIT',
      packages=['kinemathic'],
      zip_safe=False)
