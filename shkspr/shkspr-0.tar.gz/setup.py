from setuptools import setup

__version__ = '0'
with open('README.md', 'r') as fl:
    long_desc = fl.read()

setup(name='shkspr',
      version=__version__,
      description='Uses Nginx X-Accel to provide auth for microservices',
      long_description=long_desc,
      long_description_content_type='text/markdown',
      url='http://github.com/theSage21/shakespeare',
      author='Arjoonn Sharma',
      author_email='arjoonn.94@gmail.com',
      license='MIT',
      packages=['shkspr'],
      entry_points={'console_scripts': ['shkspr=shkspr.cli:main']},
      keywords=['shkspr'],
      zip_safe=False)
