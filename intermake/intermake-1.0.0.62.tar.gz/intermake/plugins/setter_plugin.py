import inspect
import warnings
from typing import Optional, Iterator

from intermake.engine.environment import MCMD
from intermake.engine.theme import Theme
from intermake.plugins.visibilities import VisibilityClass
from mhelper import reflection_helper

from mhelper.comment_helper import abstract, override, sealed, virtual

from intermake.engine.plugin import Plugin
from intermake.engine import cli_helper
from intermake.engine.constants import EThread
from mhelper.reflection_helper import FnInspect, FnArg, AnnotationInspector


def setter_command( name = None, description = None, visibility = None ):
    def __decorator( fn ):
        return __SetterPluginViaFunction( fn, name, description, visibility )
    
    
    return __decorator


@abstract
class SetterPlugin( Plugin ):
    """
    Base class for a plugin that sets values on an object.
    
    Derived class should override `get_target` to indicate the target that will be manipulated.
    May also optionally override `set_target` if the target needs saving after modification.
    """
    
    
    class FieldedArg( FnArg ):
        def __init__( self, name: str, annotation: AnnotationInspector, default: Optional[object], description: Optional[str], field: str ):
            super().__init__( name, annotation, default, description )
            self.field = field
    
    
    def __init__( self, name: str, description: str, visibility: Optional[VisibilityClass] = None ):
        """
        Constructor. Takes the normal plugin arguments
        :param name: See `Plugin` 
        :param description: See `Plugin`   
        :param visibility: See `Plugin` 
        """
        super().__init__( names = name,
                          description = description,
                          threading = EThread.SINGLE,
                          visibility = visibility )
        
        self.__populated = False
    
    
    @virtual
    def format_key( self, key: str ) -> Optional[str]:
        """
        Given the `key` property, returns the name of the associated parameter, or `None` if the parameter should be hidden.
        The default implementation returns the key verbatim.
        """
        return key
    
    
    @abstract
    def get_sample( self ) -> object:
        """
        Obtains the sample object from which the available properties should be deduced.
        This is called only once - the first time the plugin is run (`on_run`) or the help text (`description`) is requested. 
        :return: 
        """
        raise NotImplementedError( "abstract" )
    
    
    @property
    def args( self ):
        self.__populate()
        return super().args
    
    
    def __populate( self ):
        """
        Called to populate the lookup table `__argument_to_property`.
        """
        if self.__populated:
            return
        
        sample = self.get_sample()
        
        for arg, field in self.extract_arguments( sample, self.format_key ):
            self._add_argument( arg )
        
        self.__populated = True
    
    
    @classmethod
    def extract_arguments( cls, sample, formatter = str ) -> Iterator[FieldedArg]:
        """
        Extracts the arguments from a sample's fields.
        :param sample: 
        :param formatter: 
        :return: List of `FieldedArg` objects.
        """
        
        if sample is None:
            return
        
        documentation_dict = { }
        
        for x in inspect.getmro( type( sample ) ):
            documentation_dict.update( reflection_helper.extract_documentation( x.__doc__, "attr" ) )
        
        for field_name, field_value in sample.__dict__.items():
            if field_name.startswith( "_" ):
                continue
            
            argument_name = formatter( field_name )
            
            if not argument_name:
                continue
            
            documentation = documentation_dict.get( field_name )
            
            if documentation is None:
                msg = "A SetterPlugin references the field " + Theme.ERROR_BOLD + "`{}::{}`" + Theme.RESET + " (under the name `{}`) on the sample object «{}», but does not provide any documentation for that field."
                warnings.warn( msg.format( type( sample ).__name__, field_name, argument_name, sample ), UserWarning )
                documentation = "Not documented :("
            
            annotation = type( field_value )
            default = field_value
            
            yield cls.FieldedArg( argument_name, annotation, default, documentation, field_name )
    
    
    @abstract
    def get_target( self ) -> object:
        """
        Derived class must provide the target to be modified.
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def set_target( self, target: object ):
        """
        After modification, derived class may save the target.
        """
        pass
    
    
    @sealed
    def get_description( self ):
        """
        OVERRIDE to ensure the the parameters are populated before returning the description.
        """
        return super().get_description()
    
    
    @override
    @sealed
    def on_run( self ):
        """
        Sets the specified value(s).
        """
        set_one = False
        msg = []
        target = self.get_target()
        
        for arg, value in MCMD.args.items():
            if not isinstance( arg, self.FieldedArg ):
                continue
            
            if value is not None:
                setattr( target, arg.field, value )
                msg.append( cli_helper.format_kv( arg.name, value, "-->" ) )
                set_one = True
        
        if not set_one:
            for field_name in sorted( target.__dict__.keys() ):
                name = self.format_key( field_name )
                msg.append( cli_helper.format_kv( name, target.__dict__[field_name] ) )
        else:
            self.set_target( MCMD, target )
        
        MCMD.information( "\n".join( msg ) )


class __SetterPluginViaFunction( SetterPlugin ):
    def get_sample( self ) -> object:
        return self.function.return_type
    
    
    def get_target( self ) -> object:
        kwargs = MCMD.args.tokwargs()
        
        for arg in MCMD.args:
            if isinstance(arg, self.FieldedArg ):
                del kwargs[arg.name]
        
        return self.function.call( **kwargs )
    
    
    def __init__( self, fn, name: Optional[str], description: Optional[str], visibility: Optional[VisibilityClass] ):
        self.function = FnInspect( fn )
        
        if self.function.return_type is None:
            raise ValueError( "A setter command «{}» has been created, but the return type has not been specified. This is probably an error so the execution has been halted.".format( self.function.name ) )
        
        super().__init__( name or self.function.name, description or self.function.description, visibility )
