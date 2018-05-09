from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='azure_helper',
      version='0.1.031',
      description='Library to allow easier use of Microsoft Azure APIM through python scripts',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Environment :: Console',
          'Environment :: MacOS X'
      ],
      keywords='azure utility',
      url='http://github.com/charlesfindlay/azure_helper',
      author='Charles Findlay',
      author_email='charlesfindlay1984+coding@gmail.com',
      license='MIT',
      packages=['azure_helper'],
      install_requires=['pyyaml'],
      inclue_package_data=True,
      zip_safe=False)