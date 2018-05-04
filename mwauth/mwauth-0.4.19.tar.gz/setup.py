from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    # $ pip install mwauth
    # And where it will live on PyPI: https://pypi.org/project/mwauth/
    name='mwauth',  # Required
    version='0.4.19',  # Required
    description='maxwin auth',  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://bitbucket.org/maxwin-inc/auth/src',  # Optional
    author='cxhjet',  # Optional
    author_email='13064576@qq.com',  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='maxwin commonlib auth',  # Optional
    packages=find_packages(exclude=['test','test.*']),  # Required
    install_requires=['flask','flask_redis'],  # Optional
    include_package_data=True,
    # package_data={  # Optional
    #     '': ['*.*'],
    # },

    # data_files=[('my_data', ['data/data_file'])],  # Optional
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
    project_urls={  # Optional
        'Bug Reports':'https://bitbucket.org/maxwin-inc/auth/issues?status=new&status=open',
        'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://bitbucket.org/maxwin-inc/auth/src',
    },
)


# from setuptools import setup
# from codecs import open
# from os import path
#
# here = path.abspath(path.dirname(__file__))
#
# def readme():
#     with open(path.join(here, 'readme.md'), encoding='utf-8') as f:
#         long_description = f.read()
#     return long_description
# setup(
#     name='mwauth',
#     version='0.4.16',
#     description='maxwin auth ',
#     author='cxhjet',
#     author_email='13064576@qq.com',
#     url='https://bitbucket.org/maxwin-inc/auth/src/master/',
#     long_description=readme(),  # Optional
#     # long_description_content_type='text/markdown',  # Optional (see note above)
#     classifiers=[  # Optional
#         'Development Status :: 5 - Production/Stable',
#         'Intended Audience :: Developers',
#         'Topic :: Software Development :: Build Tools',
#         'License :: OSI Approved :: MIT License',
#         'Programming Language :: Python :: 3.5',
#         'Programming Language :: Python :: 3.6',
#     ],
#     keywords='auth',  # Optional
#     # packages=find_packages(exclude=['test']),  # Required
#     packages=['mwauth','mwauth.static.auth.css',
#               'mwauth.static.auth.fonts','mwauth.static.auth.js',
#               'mwauth.templates.auth'],
#     package_data={'': ['*.*']},
#     # include_package_data=True,
#     install_requires=['flask','flask_redis'],  # Optional
#     # project_urls={  # Optional
#     #     'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
#     #     'Funding': 'https://donate.pypi.org',
#     #     'Say Thanks!': 'http://saythanks.io/to/example',
#     #     'Source': 'https://bitbucket.org/maxwin-inc/auth/src/master/',
#     # },
# )

# # setup(
# #     name=          'mwauth',
# #     version=       '0.4.15',
# #     description=   'maxwin auth ',
# #     author     =   'cxhjet',
# #     author_email = '13064576@qq.com',
# #     url   =        'https://bitbucket.org/maxwin-inc/auth/src/master/',
# #     long_description=long_description,  # Optional
# #     long_description_content_type='text/markdown',  # Optional (see note above)
# #     packages=['mwauth','mwauth.static.auth.css',
# #               'mwauth.static.auth.fonts','mwauth.static.auth.js',
# #               'mwauth.templates.auth'],
# #     package_data={
# #         '': ['*.*']
# #     },
# #     classifiers=[
# #         'Intended Audience :: Developers',
# #         'License :: OSI Approved :: BSD License',
# #         'Operating System :: OS Independent',
# #         'Programming Language :: Python :: 3.5',
# #     ],
# #     # install_requires=[
# #     #     'flask>=0.11.1'
# #     # ],
# # )
