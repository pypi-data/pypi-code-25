from setuptools import setup, find_packages

setup(name='extraction_network',
      version='0.0.1',
      description='Create network of extractions and analyse/compare such networks',
      url='http://github.com/r-kapoor/extraction_network',
      author='Rahul Kapoor',
      author_email='rahulkap@isi.edu',
      license='MIT',
      classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
    ],
      keywords='extraction network',
      packages=find_packages(),
      install_requires=['configparser', 'csv', 'os', 'networkx', 'sklearn', 'numpy', 'collections', 'pickle', 'math'],
      python_requires='>=3',
      include_package_data=True,
      zip_safe=False)