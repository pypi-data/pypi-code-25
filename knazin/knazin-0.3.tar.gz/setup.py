from setuptools import setup

# python setup.py sdist 
# python setup.py sdist upload

# Install dependencies of package
# python setup.py develop

# Upload your distribution
# twine upload dist/*


setup(name='knazin',
      version='0.3',
      description='Knazin package',
      url='http://github.com/knazin/package',
      author='Kacper Knaz',
      author_email='knazkacper@gmail.com',
      license='GNU',
      packages=['knazin'],
      zip_safe=False)