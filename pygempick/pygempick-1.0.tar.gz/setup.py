from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pygempick', 
      version='1.0', 
      description='Open Source Batch Gold Particle Picking & Procesing for Immunogold Diagnostics',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords='IGEM immunogold gold picker EM micrograph processing correlation analysis',
      url='https://github.com/jmarsil/pygempick',
      author='Joseph Marsilla',
      author_email='joseph.marsilla@mail.utoronto.ca',
      license='MIT',
      packages=['pygempick'],
      install_requires=['numpy','pandas'],
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],)
