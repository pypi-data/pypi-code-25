"""A setuptools based setup module.

See:
https://packaging.python.org/tutorials/distributing-packages/#classifiers
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""


from setuptools import setup, find_packages
from codecs import open
import os
import pypandoc

long_description = pypandoc.convert('README.md', 'rst')
long_description = long_description.replace("\r","") # YOU  NEED THIS LINE



setup(
    name='airbnb_script',  # Required
    version='1.0.6',  # Required
    description='Fork of Best script for Real estate agencies. Django + ReactJS. Reservation calendar, Mobile version, SEO, Admin panel , Classified ads.',  # Required
    long_description=long_description,  # Optional
    # long_description_content_type='text/markdown',  # This is important!
    keywords='property vacation real estate agency script cms system website plugin widget extension library saas cms crm script themeforest wordpress woocommerce drupal instagram facebook monstertemplates python reactjs django python',

    url='https://github.com/reactpython/best_script_for_agencies',  # Optional
    author='ReactScripts',  # Optional
    author_email='imconfirmer@gmail.com',  # Optional
    download_url='https://github.com/reactpython/best_script_for_agencies',


    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    # project_urls={  # Optional
    #     'Bug Reports': 'https://github.com/reactpython/best_script_for_agencies/issues',
    #     # 'Funding': '__LINK_FUNDING__',
    #     'Donations': 'https://github.com/reactpython/best_script_for_agencies',
    #     'Source': 'https://tenerifebook.com/p/support/',
    # },

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: MacOS',
            'Operating System :: Microsoft',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Internet',
            'Topic :: Scientific/Engineering :: Information Analysis',
            ],

    license='Apache License 2.0',

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(
            exclude=['scripts','sample','data']),  # Required


    include_package_data=True,
    zip_safe=False,
    install_requires=[
            # 'Scrapy>=1.1.0',
            'requests',
            ],
    extras_require={
            ':python_version == "2.7"': [
                # 'newspaper',
                # 'future>=0.16.0',
                # 'hurry.filesize>=0.9'
            ],
            ':python_version >= "3.0"': [
                # 'newspaper3k',
            ],
            },
    entry_points={
            'console_scripts': [
                'airbnb_script = airbnb_script.airbnb_script:BESTSCRIPT',
            ],
            },


    setup_requires=['setuptools'],

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    # If using Python 2.6 or earlier, then these have to be included in
    # MANIFEST.in as well.
    package_data={  # Optional
            # 'sample': ['package_data.dat'],
    },

    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],  # Optional

)
