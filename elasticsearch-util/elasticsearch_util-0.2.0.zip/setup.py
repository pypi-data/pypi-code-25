from setuptools import setup, find_packages

setup(name='elasticsearch_util',
      version='0.2.0',
      packages=find_packages(),
      description='Pythonic ElasticSearch Logging',
      author='Gehad Shaat',
      author_email='gehad.shaath@gmail.com',
      url='https://github.com/gehadshaat/elasticsearch_util',
      py_modules=['elasticsearch_util'],
      install_requires=['elasticsearch==5.3.0'],
      license='MIT License',
      zip_safe=True,
      keywords='kibana elasticsearch',
      classifiers=[])