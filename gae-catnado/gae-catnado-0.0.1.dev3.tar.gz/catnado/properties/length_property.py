from catnado.properties import _DerivedProperty


class LengthProperty(_DerivedProperty):
  """A convenience class for recording the length of another field

  Example usage:

  >>> class TagList(db.Model):
  ...   tags = db.ListProperty(unicode, required=True)
  ...   num_tags = LengthProperty(tags)

  >>> tags = TagList(tags=[u'cool', u'zany'])
  >>> tags.num_tags
  2
  """

  def __init__(self, property, *args, **kwargs):
    """Constructor.

    Args:
      property: The property to lower-case.
    """
    super(LengthProperty, self).__init__(
      lambda self: len(property.__get__(self, type(self))),
      *args, **kwargs)