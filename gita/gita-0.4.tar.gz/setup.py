from setuptools import setup

setup(
    name='gita',
    packages=['gita',],
    version='0.4',
    description='Manage multiple git repos',
    url='https://github.com/nosarthur/gita',
    download_url='https://github.com/nosarthur/gita/archive/v0.4.tar.gz',
    keywords=['git', 'multiple'],
    author='Dong Zhou',
    author_email='zhou.dong@gmail.com',
    license='MIT',
    entry_points={
        'console_scripts':[
            'gita = gita.__main__:main'
            ]
        },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        ],
)
