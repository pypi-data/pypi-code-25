# coding: utf-8

from setuptools import setup

setup(
    name='pygig',
    version='1.0.6',
    author='lyq',
    author_email='1033020837@qq.com',
    url='https://github.com/1033020837/GitIgnoreGenerator',
    description='A command tool to generate .gitignore file.',
    packages=['pygig','gitignore'],
    install_requires=['argparse','GitPython'],
    include_package_data=True,
    package_data={"gitignore": ["gitignore/*"]},
    entry_points={
        'console_scripts': [
            'pygig=pygig:main'
        ]
    }
)