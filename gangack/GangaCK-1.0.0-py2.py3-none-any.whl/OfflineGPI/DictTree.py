
import xml.etree.cElementTree as ET
import xml.etree.ElementTree as ET2

cElement = type(ET.Element(None))  # For isinstance check below

#===============================================================================

class DictTree(object):
  """
  Provide additional functionality on __getattr__ to directly access the 
  simple tree node's attribute. Very generic for most of xml-ed data.

  Taylored to Ganga-xml data.
  """

  def __init__(self, arg):
    super( DictTree, self ).__init__()
    ## ET instance is given
    if isinstance( arg, (ET2.Element,cElement)):
      self._tree = arg

    ## Path to tree is given.
    elif isinstance( arg, basestring ):
      ## Faster iter version
      for _,elem in ET.iterparse( arg, events=('start',) ):
        if elem.tag == 'class':
          self._tree = elem 
          break
    else:
      raise ValueError('Unknown constructor arg: %r'%arg)


  def __str__(self):
    """Return member attribute "name" of itself."""
    return self.get('name')

  def __getattr__(self, key):
    # print '__getattr__: key=', key
    node = self.find('attribute[@name="%s"]'%key)  # Not recursive
    if node is None:
      # print '__getattr__, abort1', key
      # Don't use AttributeError since it'll confuse python that the earlier 
      # (property) call is missing and fallback to here with wrong intention.
      raise ValueError('Attribute not found: '+key)  
    ## Simple value
    nvalue = node.find('value')
    if nvalue is not None:
      return eval(nvalue.text)
    ## Object (Class)
    nclass = node.find('class')
    if nclass is not None:
      return DictTree(nclass)
    raise ValueError('Attribute has no value node: %r'%key)

  def __getitem__(self, key):
    ## At correct location, the dict's key is expected to be nested
    # such as MetadataDict
    return self.data[key]
    # return KeyError('Key not found: %r'%key)

  ## Delegation
  def get(self,arg):
    return self._tree.get(arg)
  def find(self, arg):
    return self._tree.find(arg)
  def findall(self, arg):
    return self._tree.findall(arg)
  def remove(self, arg):
    return self._tree.remove(arg)

#===============================================================================
