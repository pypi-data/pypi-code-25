from setuptools import setup, find_packages
from os import path

setup(
      name='STA-663-final-project',
      version=1.2,
      description='A python realization of Biclustering via Sparse Singular Value Decomposition',
      url='https://github.com/xuetongli/STA-663-final-project',
      author='Chunxiao Li, Xuetong Li',
      author_email='xl222@duke.edu',
      classifiers=[
                  'Development Status :: 3 - Alpha',
                  'Intended Audience :: Developers',
                  'Topic :: Software Development :: Libraries :: Python Modules',
                  'License :: OSI Approved :: MIT License',
                  'Programming Language :: Python :: 3',
                  'Programming Language :: Python :: 3.4',
                  'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6',
                  ],
      py_modules = ['STA-663-final-project'],
      packages=find_packages(),
      scripts = ['run_STA-663-final-project.py'],
      data_files=[('my_data', ['data/BreastCancerData.txt', 
                       'data/BreastCancerLabels.txt',
                       'data/LungCancerData.txt'])],
      python_requires='>=3',
      )