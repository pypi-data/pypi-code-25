from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="spm2olca",
    version="1.1.0",
    author="Michael Srocka",
    author_email="michael.srocka@gmail.com",
    description="SimaPro Method File to olca-schema converter",
    license="MIT",
    keywords="converter lca",
    url="https://github.com/GreenDelta/spm2olca",
    download_url='https://github.com/GreenDelta/spm2olca/tarball/v1.0.0',
    packages=['spm2olca'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'spm2olca = spm2olca:main',
        ]
    },
    package_data={'spm2olca': ["data/*.*"]},
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Topic :: Utilities",
    ]
)
