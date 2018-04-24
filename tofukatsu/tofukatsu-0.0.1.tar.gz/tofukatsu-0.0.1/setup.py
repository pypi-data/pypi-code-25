from distutils.core import setup

setup(
  name = 'tofukatsu',
  packages = [''],
  version = '0.0.1',
  description = 'Tokenization Factory.',
  author = 'Liling Tan',
  license = 'Unlicensed',
  url = 'https://github.com/alvations/tofu',
  keywords = [],
  classifiers = [],
  install_requires = ['JPype1', 'six', 'nltk',
                      'jieba', 'tinysegmenter',
                      'konlpy', 'sacremoses', 'numpy']
)
