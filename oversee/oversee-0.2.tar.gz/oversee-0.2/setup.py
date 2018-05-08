from setuptools import setup

setup(
    name='oversee',
    py_modules=['oversee'],
    version='0.2',
    description='A python utility to help manage your Ubuntu OS!',
    author='Jacob Smith',
    author_email='jacob.smith@unb.ca',
    url='http://github.com/jacsmith21/oversee',
    install_requires=[
        'click',
        'python-elevate',
        'PyYaml'
    ],
    entry_points={
        'console_scripts': ['oversee=oversee.main:main']
    }
)
