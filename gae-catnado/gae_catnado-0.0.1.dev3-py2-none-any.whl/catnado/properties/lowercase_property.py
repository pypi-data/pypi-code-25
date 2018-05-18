from catnado.properties import _DerivedProperty


class LowerCaseProperty(_DerivedProperty):
  """A convenience class for generating lower-cased fields for filtering.

  Example usage:

  >>> class Pet(db.Model):
  ...   name = db.StringProperty(required=True)
  ...   name_lower = LowerCaseProperty(name)

  >>> pet = Pet(name='Fido')
  >>> pet.name_lower
  'fido'
  """

  def __init__(self, property, *args, **kwargs):
    """Constructor.

    Args:
      property: The property to lower-case.
    """
    super(LowerCaseProperty, self).__init__(
      lambda self: property.__get__(self, type(self)).lower(),
      *args, **kwargs)