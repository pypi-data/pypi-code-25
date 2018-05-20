import os

from google.appengine.api import users
from google.appengine.ext import db


class CurrentDomainProperty(db.Property):
  """A property that restricts access to the current domain.

  Example usage:

  >>> class DomainModel(db.Model):
  ...   domain = CurrentDomainProperty()

  >>> os.environ['HTTP_HOST'] = 'domain1'
  >>> model = DomainModel()

  The domain is set automatically:

  >>> model.domain
  u'domain1'

  You cannot change the domain:

  >>> model.domain = 'domain2'  # doctest: +ELLIPSIS
  Traceback (most recent call last):
      ...
  InvalidDomainError: Domain 'domain1' attempting to illegally access data for domain 'domain2'

  >>> key = model.put()
  >>> model = DomainModel.get(key)
  >>> model.domain
  u'domain1'

  You cannot write the data from another domain:

  >>> os.environ['HTTP_HOST'] = 'domain2'
  >>> model.put() # doctest: +ELLIPSIS
  Traceback (most recent call last):
      ...
  InvalidDomainError: Domain 'domain2' attempting to allegally modify data for domain 'domain1'

  Nor can you read it:

  >>> DomainModel.get(key)  # doctest: +ELLIPSIS
  Traceback (most recent call last):
      ...
  InvalidDomainError: Domain 'domain2' attempting to illegally access data for domain 'domain1'

  Admin users can read and write data for other domains:

  >>> os.environ['USER_IS_ADMIN'] = '1'
  >>> model = DomainModel.get(key)
  >>> model.put()  # doctest: +ELLIPSIS
  datastore_types.Key.from_path(u'DomainModel', ...)

  You can also define models that should permit read or write access from
  other domains:

  >>> os.environ['USER_IS_ADMIN'] = '0'
  >>> class DomainModel2(db.Model):
  ...   domain = CurrentDomainProperty(allow_read=True, allow_write=True)

  >>> model = DomainModel2()
  >>> model.domain
  u'domain2'
  >>> key = model.put()

  >>> os.environ['HTTP_HOST'] = 'domain3'
  >>> model = DomainModel2.get(key)
  >>> model.put()  # doctest: +ELLIPSIS
  datastore_types.Key.from_path(u'DomainModel2', ...)
  """

  def __init__(self, allow_read=False, allow_write=False, *args, **kwargs):
    """Constructor.

    Args:
      allow_read: If True, allow entities with this property to be read, but not
        written, from other domains.
      allow_write: If True, allow entities with this property to be modified
        from other domains.
    """
    self.allow_read = allow_read
    self.allow_write = allow_write
    super(CurrentDomainProperty, self).__init__(*args, **kwargs)

  def __set__(self, model_instance, value):
    if not value:
      value = unicode(os.environ['HTTP_HOST'])
    elif (value != os.environ['HTTP_HOST'] and not self.allow_read and
          not users.is_current_user_admin()):
      raise InvalidDomainError(
        "Domain '%s' attempting to illegally access data for domain '%s'"
        % (os.environ['HTTP_HOST'], value))
    super(CurrentDomainProperty, self).__set__(model_instance, value)

  def get_value_for_datastore(self, model_instance):
    value = super(CurrentDomainProperty, self).get_value_for_datastore(
      model_instance)
    if (value != os.environ['HTTP_HOST'] and
        not users.is_current_user_admin() and
        not self.allow_write):
      raise InvalidDomainError(
        "Domain '%s' attempting to allegally modify data for domain '%s'"
        % (os.environ['HTTP_HOST'], value))
    return value


class InvalidDomainError(Exception):
  """Raised when something attempts to access data belonging to another domain."""
  pass
