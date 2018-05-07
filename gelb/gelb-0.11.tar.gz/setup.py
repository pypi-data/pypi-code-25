from subprocess import check_output
from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

def get_next_version():
    stdoutdata = check_output(['yolk', '-V', 'gelb'])
    last_version = stdoutdata.split()[-1]
    new_version = str(float(last_version) + 0.01)
    return new_version

setup(name='gelb',
      version=get_next_version(),
      description='Compiler for the GeLB Description (GD) programming language',
      long_description=readme(),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development :: Code Generators',
          'Topic :: Software Development :: Compilers',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Scientific/Engineering :: Mathematics'
      ],
      keywords='LB LBM CFD compilers fluid-dynamics',
      url='http://github.com/dchirila/gelb',
      author='Dragos B. Chirila',
      author_email='dchirila@gmail.com',
      license='MIT',
      packages=['gelb'],
      install_requires=[
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      entry_points={
          'console_scripts': ['gelbc=gelb.gelbc:main'],
      },
      zip_safe=False)
