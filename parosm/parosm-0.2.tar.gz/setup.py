import unittest
from setuptools import setup, find_packages


def spin_up_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests')
    return test_suite


if __name__ == '__main__':
    with open('README.rst', 'r') as f:
        long_description = f.read()

    setup(
        name='parosm',
        version='0.2',
        description='OpenStreetMap Parser',
        long_description=long_description,
        url='https://github.com/DaGuich/parosm.git',
        keywords=[
            'parser',
            'osm',
            'openstreetmap'
        ],
        license='GPL Version 3',
        classifiers=[
            'Programming Language :: Python :: 3'
        ],
        packages=find_packages(exclude=['tests']),
        install_requires=[
            'protobuf',
            'defusedxml==0.5.0',
            'python-magic==0.4.15'
        ],
        entry_points={
            'console_scripts': [
                'osm2sql = parosm.prog.osm2sql.__init__:main',
                'osminfo = parosm.prog.osminfo.__init__:main'
            ]
        },
        test_suite='setup.spin_up_test_suite',
        python_requires='>=3.0.0',
    )
