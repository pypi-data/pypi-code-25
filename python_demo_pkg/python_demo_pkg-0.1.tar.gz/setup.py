from setuptools import setup, find_packages
setup(
    name="python_demo_pkg",
    version="0.1",
    packages=find_packages(),
    scripts=[],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['requests'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author="David Crocker",
    author_email="dwcrocker@outlook.com",
    description="This is an Example Package",
    license="MIT",
    keywords="mydemo example",
    url="http://crocker-webapps.com",   # project home page, if any
    project_urls={
    }

    # could also include long_description, download_url, classifiers, etc.
)