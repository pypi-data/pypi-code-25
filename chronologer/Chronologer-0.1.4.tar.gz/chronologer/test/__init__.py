import cherrypy

from clor import configure

from .. import bootstrap, envconf


def setUpModule():
  cherrypy.config.update({'environment': 'test_suite'})
  config = configure(*getattr(envconf, 'test_suite'))
  bootstrap(config)

