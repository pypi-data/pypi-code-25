from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup
import sys

def main():
    install_list = ['networkx==1.11', 'numpy']

    setup(name='paths_graph',
          version='0.0.1',
          description='Algorithm for analyzing paths in directed graphs.',
          long_description='The Paths Graph is a data structure derived from '
                           'a directed graph that can be used to represent '
                           'and analyze ensembles of directed (and possibly '
                           'signed) paths.',
          author='John A. Bachman',
          author_email='john_bachman@hms.harvard.edu',
          url='https://github.com/johnbachman/paths_graph',
          classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            ],
          keywords=['graph', 'network', 'path', 'pathway', 'sampling',
                    'ensemble'],
          #project_urls={'Documentation': 'https://paths_graph.readthedocs.io'},
          packages=['paths_graph'],
          install_requires=install_list,
          #tests_require=['nose'],
          include_package_data=True,
        )


if __name__ == '__main__':
    main()
