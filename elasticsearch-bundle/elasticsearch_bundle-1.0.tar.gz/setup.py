from distutils.core import setup
setup(
  name='elasticsearch_bundle',
  packages=['elasticsearch_bundle'],
  version='1.0',
  description='elasticsearch_bundle support for applauncher',
  author='Alvaro Garcia Gomez',
  author_email='maxpowel@gmail.com',
  url='https://github.com/applauncher-team/elasticsearch_bundle',
  download_url='https://github.com/maxpowel/elasticsearch_bundle/archive/master.zip',
  keywords=['elasticsearch', 'applauncher'],
  classifiers=['Topic :: Adaptive Technologies', 'Topic :: Software Development', 'Topic :: System', 'Topic :: Utilities'],
  install_requires=['applauncher', 'elasticsearch']
)
