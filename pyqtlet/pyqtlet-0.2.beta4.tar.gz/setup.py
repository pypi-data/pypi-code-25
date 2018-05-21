from distutils.core import setup
setup(
  name = 'pyqtlet',
  packages = ['pyqtlet', 
      'pyqtlet.web', 
      'pyqtlet.web.modules.leaflet', 
      'pyqtlet.leaflet', 
      'pyqtlet.leaflet.core'],
  version = '0.2.beta4',
  description = 'Using leaflet maps in PyQt',
  author = 'Samarth Hattangady',
  author_email = 'samhattangady@gmail.com',
  url = 'https://github.com/skylarkdrones/pyqtlet',
  keywords = ['leaflet', 'pyqt', 'maps'],
  classifiers = [],
)
