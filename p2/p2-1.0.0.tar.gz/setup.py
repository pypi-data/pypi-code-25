import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()


setup(
    name='p2',
    version='1.0.0',
    description='Rerun command by watching modified file',
    long_description=README,
    url='https://github.com/keitheis/p2',
    author='Keith Yang',
    author_email='yang@keitheis.org',
    license='MIT License',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='keitheis',
    packages=find_packages(exclude=['tests*']),
    install_requires=[''],
    entry_points={
        'console_scripts': [
            'p2=p2.cmd:main',
        ],
    },
)
