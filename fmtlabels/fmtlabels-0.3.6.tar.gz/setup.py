from setuptools import setup

setup(
    name='fmtlabels',
    version='0.3.6',
    description='labels formatting from csv/xlsx to json',
    url='http://bitbucket.org/yimian/fmtlabels',
    packages=['fmtlabels'],
    install_requires=[
        'tablib>=0.12',
        'requests>=2.18',
    ],
    scripts=['bin/fmtlbl'],
    zip_safe=False
)
