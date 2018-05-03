from setuptools import setup, find_packages

setup(
    name='gc-content',
    version='0.0.1',
    description=("gc-content is a command-line tool that will calculate"
                 "the GC content (%) of each primer in a FASTA file"),
    url='https://eexwhyzee.github.io',
    author='Minh Hoang',
    author_email='eexwhyzee@gmail.com',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3',
    install_requires=['biopython==1.71'],
    entry_points={
        'console_scripts': ['gc-content=gc_content.app:main']},
    test_suite='nose.collector',
    tests_require=['nose']
)
