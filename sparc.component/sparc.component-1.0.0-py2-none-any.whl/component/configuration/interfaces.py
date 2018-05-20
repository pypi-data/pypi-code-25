from zope import interface

class ISparcPreparedConfigurationContext(interface.Interface):
    """Marker for a zope.configuration.interfaces.IConfigurationContext
    that has been prepared for zcml processing
    """