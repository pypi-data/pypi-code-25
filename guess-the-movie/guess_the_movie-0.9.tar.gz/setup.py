from setuptools import setup, find_packages

setup(
    name='guess_the_movie',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    version='0.9',
    license='MIT',
    install_requires=[
        'pyqt5',
    ],
    description='Game guess the movie by screenshot',
    author='Alexey',
    author_email='bagar0x60@gmail.com',
    url='https://github.com/moevm/gui-1h2018-34', # use the URL to the github repo
    package_data={
        # And include any *.msg files found in the 'hello' package, too:
        'guess_the_movie': ['data/*'],
    },
    entry_points={
        'console_scripts': [
            'guess-the-movie=guess_the_movie.main:main',
        ],
    },
)