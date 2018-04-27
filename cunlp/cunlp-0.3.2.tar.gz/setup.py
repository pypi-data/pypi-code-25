from setuptools import setup, find_packages

setup(
  name = 'cunlp',
  packages = find_packages(),
  package_data = {'cunlp': ['_embedding','_model_tokenizer','_model_pos_map','_model_pos']},
  version = '0.3.2',
  description = 'Chulalongkorn University Natural Languages Processing Library (Beta)',
  author = 'Danupat Khamnuansin, Nuttasit Mahakusolsirikul',
  author_email = 'danupat.K@student.chula.ac.th, nuttasit.M@student.chula.ac.th',
  url = 'https://github.com/jrkns/cunlp',
  download_url = 'https://github.com/jrkns/cunlp/dist/0.3.2.tar.gz',
  keywords = ['nlp', 'thai'],
  classifiers = [],
  install_requires=[
    'numpy>=1.14.1',
    'Keras==2.1.5',
    'h5py>=2.7.1'
  ]
)