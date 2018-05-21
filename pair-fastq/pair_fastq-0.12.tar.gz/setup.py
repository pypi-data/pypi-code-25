from setuptools import setup

setup(
    name='pair_fastq',
    author='jlevy44',
    version='0.12',
    py_modules=['pair_fastq'],
    install_requires=[
        'pandas',
	'numpy',
	'click'
    ],
    entry_points="""
        [console_scripts]
        pairfastq=pair_fastq:pairfastq"""
)
