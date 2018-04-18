from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = open('VERSION','r').read()

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='fidentify',
    version=__version__,
    description="Python Script to identify faces in a video. It is a ready-to-run code! ",
    long_description=long_description,
    url='https://github.com/NoSkillGuy/fidentify',
    download_url='https://github.com/NoSkillGuy/fidentify/tarball/' + __version__,
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='face-recognition face-detection face detection recognition terminal command-line work',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Siva Praveen Rayapudi',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='rsivapraveen001@gmail.com',
    entry_points={
        'console_scripts': [
            'fidentify = fidentify.fidentify:main'
        ]}
)
