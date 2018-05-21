from setuptools import setup, find_packages

setup(name='loess',
      version='2.0.11',
      description='LOESS: Local Regression Smoothing in One or Two Dimensions',
      long_description=open("README.rst").read(),
      url='http://purl.org/cappellari/software',
      author='Michele Cappellari',
      author_email='michele.cappellari@physics.ox.ac.uk',
      license='Other/Proprietary License',
      packages=find_packages(),
      install_requires=['numpy', 'matplotlib', 'plotbin'],
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "Intended Audience :: Science/Research",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3"],
      zip_safe=True)
