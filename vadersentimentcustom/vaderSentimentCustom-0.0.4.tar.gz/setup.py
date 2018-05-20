from setuptools import setup, find_packages
setup(
    name = 'vaderSentimentCustom',
    version = '0.0.4',
    description = 'FirmValue customized vaderSentiment version',
    license='MIT',
    author = 'Ryszard Gwozdowski',
    author_email = 'ryszard.gwozdowski@firmvalue.pl',
    keywords=['vader', 'customized', 'Python2'],
    packages = ['vaderSentimentCustom'],
    package_data = {
        # If any package contains *.txt files, include them:
        '': ['*.txt'],
    }
)