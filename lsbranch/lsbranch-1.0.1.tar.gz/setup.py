from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='lsbranch',
    version="1.0.1",

    description='List all directories with .git subdirectory and show current branch for each.',
    long_description=readme(),
    long_description_content_type='text/markdown',

    url='https://github.com/arrrlo/lsbranch',
    licence='MIT',

    author='Ivan Arar',
    author_email='ivan.arar@gmail.com',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='git, branch, ls',

    packages=['lsbranch'],
    install_requires=[
        'click==6.3',
        'colorama~=0.3',
        'pyfiglet~=0.7.5',
        'termcolor~=1.1.0',
    ],

    entry_points={
        'console_scripts': [
            'lsbranch=lsbranch.cli:cli'
        ],
    },

    project_urls={
        'Source': 'https://github.com/arrrlo/lsbranch',
    },
)
