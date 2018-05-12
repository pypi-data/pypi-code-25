from setuptools import setup, find_packages

from tx import __version__

long_description = open('README.md').read()

setup(
    name='tx',
    version=__version__,
    description='An extension base for twisted',
    author='Yehuda Deutsch',
    author_email='yeh@uda.co.il',

    license='MIT',
    url='https://gitlab.com/uda/tx/',
    project_urls={
        'Source': 'https://gitlab.com/uda/tx/',
    },
    keywords='twisted extension',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Twisted',
        'Framework :: Zope',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
