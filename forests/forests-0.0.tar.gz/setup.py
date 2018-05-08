from setuptools import setup

__version__ = ['0.0']
requirements = ['sklearn', 'numpy', 'scipy']

setup(name='forests',
      version='.'.join(__version__),
      description='Variations on Random Forests for classification / regression',
      url='http://gitlab.com/theSage21/forests',
      author='Arjoonn Sharma',
      author_email='arjoonn.94@gmail.com',
      packages=['forests'],
      install_requires=requirements,
      keywords=['forests', 'random forests', 'decision stream', 'decision jungle'],
      zip_safe=False)
