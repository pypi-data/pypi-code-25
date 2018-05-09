from distutils.core import setup

setup(
    name = 'speechdb',
    packages = ['speechdb'],
    version = '0.1.4',
    description = 'A library that simplifies the usability of the predominant speech databases.',
    long_description = """
    # Speech DB Engine

    ### A project that simplifies the usability of the predominant speech databases.

    ## Getting Started

    ### Download from Pypi

    ```bash
    pip install speechdb
    ```

    ### General Syntax

    ```python
    from speechdb import timit
    # core_test_csv can be found in the testing_sets directory
    timit1 = timit.Timit(path_to_timit_database,path_to_core_test_csv)
    # yType: {'PHN','DLCT','SPKR'} (default='PHN')
    # yVals: 'All' or ['sh',...] or ['DR1',...] or ['FDAB0',...] (default='All')
    # dataset: {'test','train','coretest') (default='train')
    y,x = timit1.read_db(yType, yVals, dataset)
    # ex.
    y,x = timit1.read_db('PHN',['sh'],'test')
    ```
    """,
    author = 'Yuan Gong',
    author_email = 'yuan.gong.12@nd.edu',
    url = 'https://github.com/YuanGongND/Speech_DB_Engine',
    download_url = 'https://github.com/YuanGongND/Speech_DB_Engine/archive/0.1.tar.gz',
    keywords = ['speech', 'research'],
    classifiers = [],
)
