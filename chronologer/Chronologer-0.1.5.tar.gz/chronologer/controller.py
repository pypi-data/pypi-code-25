from datetime import datetime, timezone
from http import HTTPStatus

import cherrypy

from .model import createRecord, groupTimeseries


__all__ = 'RecordApi', 'authenticate'


class RecordApi:

  exposed = True


  def _getDt(self, s):
    if not s:
      return None

    try:
      return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo = timezone.utc)
    except ValueError:
      return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo = timezone.utc)

  def _getFilters(self, **kwargs):
    return {
      'date'  : (self._getDt(kwargs.get('after')), self._getDt(kwargs.get('before'))),
      'level' : kwargs.get('level'),
      'name'  : kwargs.get('name'),
      'query' : kwargs.get('query')
    }

  def HEAD(self, **kwargs):
    filters = self._getFilters(**kwargs)
    group   = kwargs.get('group')
    tz      = kwargs.get('timezone')
    if group and timezone:
      m15grp = cherrypy.request.app.storage.count(filters, True)
      result = groupTimeseries(m15grp, group, tz)
      pair   = list(map(','.join, zip(*((str(int(v[0].timestamp())), str(v[1])) for v in result))))

      headers = cherrypy.response.headers
      headers['X-Record-Group'], headers['X-Record-Count'] = pair if pair else ('', '')
    else:
      cherrypy.response.headers['X-Record-Count'] = cherrypy.request.app.storage.count(filters)

    cherrypy.response.headers['Cache-Control'] = 'no-cache'

  @cherrypy.tools.jsonify
  def GET(self, _id = None, **kwargs):
    storage = cherrypy.request.app.storage
    if _id:
      record = storage.get(_id)
      cherrypy.response.headers['Cache-Control'] = 'max-age=2600000'
      return record
    else:
      filters = self._getFilters(**kwargs)
      range = storage.range(int(kwargs['left']), int(kwargs['right']), filters)
      cherrypy.response.headers['Cache-Control'] = 'no-cache'
      return range

  @cherrypy.tools.jsonify
  def POST(self, **kwargs):
    id = cherrypy.request.app.storage.record(*createRecord(**kwargs))
    cherrypy.response.status = HTTPStatus.CREATED.value  # @UndefinedVariable
    return id

