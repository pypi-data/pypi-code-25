import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='ocmpy',
    version='0.1.3',
    author='Jeremy Banker',
    author_email='loredous@loredous.net',
    description='Python API wrapper for the Open Charge Map for EV charging stations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/loredous/ocmpy',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ),
    install_requires=[
        'requests',
    ],
)
