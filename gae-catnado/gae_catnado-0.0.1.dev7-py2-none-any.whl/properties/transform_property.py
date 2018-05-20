from google.appengine.ext import db


def TransformProperty(source, transform_func=None, *args, **kwargs):
  """Implements a 'transform' datastore property.

  TransformProperties are similar to DerivedProperties, but with two main
  differences:
  - Instead of acting on the whole model, the transform function is passed the
    current value of a single property which was specified in the constructor.
  - Property values are calculated when the property being derived from is set,
    not when the TransformProperty is fetched. This is more efficient for
    properties that have significant expense to calculate.

  TransformProperty can be declared as a regular property, passing the property
  to operate on and a function as the first arguments, or it can be used as a
  decorator for the function that does the calculation, with the property to
  operate on passed as an argument.

  Example:

  >>> class DatastoreFile(db.Model):
  ...   name = db.StringProperty(required=True)
  ...
  ...   data = db.BlobProperty(required=True)
  ...   size = TransformProperty(data, len)
  ...
  ...   @TransformProperty(data)
  ...   def hash(val):
  ...     return hashlib.sha1(val).hexdigest()

  You can read transform properties the same way you would regular ones:

  >>> file = DatastoreFile(name='Test.txt', data='Hello, world!')
  >>> file.size
  13
  >>> file.data
  'Hello, world!'
  >>> file.hash
  '943a702d06f34599aee1f8da8ef9f7296031d699'

  Updating the property being transformed automatically updates any
  TransformProperties depending on it:

  >>> file.data = 'Fubar'
  >>> file.data
  'Fubar'
  >>> file.size
  5
  >>> file.hash
  'df5fc9389a7567ddae2dd29267421c05049a6d31'

  Attempting to set a transform property directly will throw an error:

  >>> file.size = 123
  Traceback (most recent call last):
      ...
  DerivedPropertyError: Cannot assign to a TransformProperty

  When persisted, transform properties are stored to the datastore, and can be
  filtered on and sorted by:

  >>> file.put() # doctest: +ELLIPSIS
  datastore_types.Key.from_path(u'DatastoreFile', ...)

  >>> DatastoreFile.all().filter('size =', 13).get().hash
  '943a702d06f34599aee1f8da8ef9f7296031d699'
  """
  if transform_func:
    # Regular invocation
    return _TransformProperty(source, transform_func, *args, **kwargs)
  else:
    # We're being called as a decorator with arguments
    def decorate(decorated_func):
      return _TransformProperty(source, decorated_func, *args, **kwargs)

    return decorate


class _TransformProperty(db.Property):
  def __init__(self, source, transform_func, *args, **kwargs):
    """Constructor.

    Args:
      source: The property the transformation acts on.
      transform_func: A function that takes the value of source and transforms
        it in some way.
    """
    super(_TransformProperty, self).__init__(*args, **kwargs)
    self.source = source
    self.transform_func = transform_func

  def __orig_attr_name(self):
    return '_ORIGINAL' + self._attr_name()

  def __transformed_attr_name(self):
    return self._attr_name()

  def __get__(self, model_instance, model_class):
    if model_instance is None:
      return self
    last_val = getattr(model_instance, self.__orig_attr_name(), None)
    current_val = self.source.__get__(model_instance, model_class)
    if last_val == current_val:
      return getattr(model_instance, self.__transformed_attr_name())
    transformed_val = self.transform_func(current_val)
    setattr(model_instance, self.__orig_attr_name(), current_val)
    setattr(model_instance, self.__transformed_attr_name(), transformed_val)
    return transformed_val

  def __set__(self, model_instance, value):
    raise db.DerivedPropertyError("Cannot assign to a TransformProperty")
