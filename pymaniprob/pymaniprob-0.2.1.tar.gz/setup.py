from setuptools import setup, find_packages

setup(name='pymaniprob',
      version='0.2.1',
      author='Daniel Tait',
      author_email='tait.djk@gmail.com',
      url='http://github.com/danieljtait/pymaniprob',
      license='MIT',
      packages=find_packages(),
      install_requires=['numpydoc', 'numpy', 'matplotlib', 'scipy'],
      zip_safe=False)
