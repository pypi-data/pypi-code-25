from zope.component.factory import Factory
from zope import interface

class ISparcTest(interface.Interface):
    """Test interface"""

@interface.implementer(ISparcTest)
class SparcTest():
    pass
SparcTestFactory = Factory(SparcTest)