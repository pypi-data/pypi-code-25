import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

readme_path = os.path.join(os.path.dirname(__file__), 'README.md')

try:
    import pypandoc
    long_description = pypandoc.convert(readme_path, 'rst')
except ImportError:
    long_description = open(readme_path).read()

setup(
    name='django-simple_perms',
    version='0.2.5',
    packages=find_packages(),
    install_requires=['django'],
    include_package_data=True,
    license='WTFPL',
    description='A simple class based permission backend for django',
    long_description=long_description,
    url='https://bitbucket.org/hespul/django-simple_perms',
    author='Fabien MICHEL',
    author_email='fabien.michel@hespul.org',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
