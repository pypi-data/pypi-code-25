from zope import interface
from zope.configuration import xmlconfig, config
from zope.configuration.interfaces import IConfigurationContext
from sparc.config import IConfigContainer
from .interfaces import ISparcPreparedConfigurationContext

@interface.implementer(IConfigurationContext)
class PreparedConfigurationMachine(object):
    """A prepared configuration machine that is ready for feature and zcml
    entry point assignments
    """
    def __new__(self, features=None):
        context = config.ConfigurationMachine()
        xmlconfig.registerCommonDirectives(context)
        for feature in (features or []):
            context.provideFeature(feature)
        interface.alsoProvides(context, ISparcPreparedConfigurationContext)
        return context

def handle_sparc_component_config_value(context, value):
        """Update a ConfigurationMachine state with ZopeComponentConfiguration
        YAML value specs
        
        Applies features and zcml entry points as specified by *value* which
        is a mapping with a schema that matches 
        configure.yaml:ZopeComponentConfiguration to the given *context*
        
        Args:
            context: ISparcPreparedConfigurationContext provider
            value: mapping with ZopeComponentConfiguration YAML value specs
        """
        assert ISparcPreparedConfigurationContext.providedBy(context)
        for feature in value.get('features', []):
            context.provideFeature(feature)
        
        for spec in value.get('zcml', []):
            xmlconfig.file(spec.get('file', 'configure.zcml'), 
                           spec.get('package', None), 
                           context=context, 
                           execute=False)
    

def handle_sparc_component_config_container(config_container, first=False, context=None):
    """Process Zope Component configurations
    
    Args:
        config_container: sparc.config.IConfigContainer provider
    
    Kwargs:
        first: True indicates to only process the first 
               ZopeComponentConfiguration found in config_container
        context: A zope.configuration.config.ConfigurationMachine() instance.
                 A new one will be generated if not provided.
    """
    assert IConfigContainer.providedBy(config_container)
    context = context or PreparedConfigurationMachine()
    for value in config_container.sequence('ZopeComponentConfiguration'):
        handle_sparc_component_config_value(context, value)
    context.execute_actions()
