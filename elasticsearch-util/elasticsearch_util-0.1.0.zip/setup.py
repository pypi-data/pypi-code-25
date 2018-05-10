from setuptools import setup, find_packages

setup(name='elasticsearch_util',
      version='0.1.0',
      packages=find_packages(),
      description='Pythonic ElasticSearch Logging',
      author='Gehad Shaat',
      author_email='gehad.shaat@intel.com',
      url='https://github.intel.com/gshaat/elasticsearch_util',
      py_modules=['elasticsearch_util'],
      install_requires=['elasticsearch==5.3.0'],
      license='MIT License',
      zip_safe=True,
      keywords='kibana elasticsearch',
      classifiers=[])