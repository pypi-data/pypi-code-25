from setuptools import setup, find_packages

setup(name='plotbin',
      version='3.1.1',
      description='Plotting Binned Maps and Other Utilities',
      long_description=open("README.rst").read(),
      url='http://purl.org/cappellari/software',
      author='Michele Cappellari',
      author_email='michele.cappellari@physics.ox.ac.uk',
      license='Other/Proprietary License',
      packages=find_packages(),
      install_requires=['numpy', 'scipy', 'matplotlib'],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Science/Research",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3"],
      zip_safe=True)
