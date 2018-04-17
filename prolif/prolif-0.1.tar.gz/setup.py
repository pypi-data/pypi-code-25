from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='prolif',
      version='0.1',
      description='Protein-Ligand Interaction Fingerprints',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://github.com/cbouy/ProLIF',
      author='Cédric Bouysset',
      author_email='bouysset.cedric@gmail.com',
      license='Apache License, Version 2.0',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
      ],
      keywords='science chemistry biology drug-design chemoinformatics virtual-screening',
      packages=['prolif'],
      entry_points = {
        'console_scripts': ['prolif=prolif.command_line:cli'],
        },
      dependency_links=['https://github.com/rdkit/rdkit'],
      include_package_data=True,
      zip_safe=False)
