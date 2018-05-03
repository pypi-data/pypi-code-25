from distutils.core import setup


setup(
    name='MKGen',
    version='0.0.6',
    description='Text generator using the Markov model',
    author='Mio Kato',
    author_email='miokato07@gmail.com',
    url='https://github.com/miokato/MarkovGenerator',
    install_requires=['numpy', 'mecab-python3'],
    packages=['MKGen'],
)