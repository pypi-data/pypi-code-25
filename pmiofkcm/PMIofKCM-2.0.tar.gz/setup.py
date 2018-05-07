from distutils.core import setup

setup(
    name = 'PMIofKCM',
    packages = ['PMIofKCM'],
    package_dir={'PMIofKCM':'PMIofKCM'},
    package_data={'PMIofKCM':['management/commands/*']},
    version = '2.0',
    description = 'PMIofKCM for KCM',
    author = 'davidtnfsh',
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/UDICatNCHU/PMIofKCM',
    download_url = 'https://github.com/UDICatNCHU/PMIofKCM/archive/v2.0.tar.gz',
    keywords = ['pmi',],
    classifiers = [],
    license='GPL3.0',
    install_requires=[
        'pymongo',
        'ngram'
    ],
    zip_safe=True
)
