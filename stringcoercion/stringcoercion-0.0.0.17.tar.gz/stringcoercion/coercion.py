"""
Module for dealing with coercing values to strings.
See `readme.md` in the project root for details.
"""

from enum import Enum
from traceback import format_exc
from typing import List, Optional, Sequence, Tuple, Type, cast

import itertools

from mhelper import AnnotationInspector, Password, array_helper, ignore, string_helper, ansi, abstract, virtual


class CoercionInfo:
    """
    :data collection:           Calling coercer collection
    :data annotation:           An `AnnotationInspector`, providing information on the intended format to coerce into.
    :data source:               Value to translate from. Undefined during queries inside the `can_handle` function.
    :data cancel:               Setting this to `True` prevents further `AbstractCoercer`s trying to covert this value to this annotation (other annotations may still proceed).
    """
    
    
    def __init__( self, annotation: AnnotationInspector, collection: Optional["CoercerCollection"], source: Optional[str] ):
        """
        CONSTRUCTOR
        See class comments for parameters.
        """
        self.collection = collection
        self.annotation = annotation
        self.source = source
        self._cancelled = False
    
    
    def __str__( self ):
        return "Coerce «{}» into {}".format( self.source, self.annotation )


class CoercionError( Exception ):
    """
    Raised when an individual AbstractCoercer fails, and also when all coercers have failed.
    """
    
    
    def __init__( self, message: str, cancel: bool = False ):
        super().__init__( message )
        self.cancel = cancel


@abstract
class AbstractCoercer:
    """
    Coercer base class.
    
    The abstract methods must be overridden.
    Additionally derived classes should provide a doc string detailing the format the coercer handles.
    """
    
    
    class PRIORITY:
        """
        Priorities namespace.
        
        :data _NONE:       AbstractCoercer is unused. Equivalent to `None` and `False`.
        :data _HIGHEST:    Highest valid priority (lowest value).
        :data _LOWEST:     Lowest expected (highest value).
        :data HIGH:        A priority above the default
        :data DEFAULT:     The default recommended priority for user coercers. Equivalent to `True`.
        :data INBUILT:     The priority used by the inbuilt coercers, which is lower than DEFAULT.
        :data FALLBACK:    The priority used by the fallback coercer. No priority should be lower.
        """
        _NONE = 0
        _HIGHEST = 1
        SKIP = 0
        HIGH = 25
        DEFAULT = 50
        INBUILT = 75
        LOW = 75
        FALLBACK = 100
        _LOWEST = 100
    
    
    @abstract
    def can_handle( self, info: CoercionInfo ) -> int:
        """
        ABSTRACT
        Determines if the coercer can handle this coercion.
        
        :param info:    Details on the coercion. The `source` field is indeterminate during the query and should be ignored. 
        :return:        An `int` above 1 denoting the priority of this coercer in relation to the others, or 0 if this coercer
                        cannot handle the provided data. 
        """
        raise NotImplementedError( "abstract" )
    
    
    @abstract
    def coerce( self, info: CoercionInfo ) -> Optional[object]:
        """
        ABSTRACT
        Performs the actual coercion.
        This will only ever be called if `can_handle` returned a non-zero value previously.
        
        :param info:            Details on the coercion to perform. 
        :return:                The object in the designated type or format.
        :except CoercionError:  This error should be raised if the coercion cannot be performed.
                                The next coercer in the queue will then be attempted unless the error has the `cancel` flag set.
                                Other error types should not be returned as they will be considered a logic, rather than input,
                                error.
        """
        raise NotImplementedError( "abstract" )
    
    
    def __str__( self ):
        return type( self ).__name__


class _Coercion:
    def __init__( self, priority, info, coercer ):
        self.priority = priority
        self.info = info
        self.coercer = coercer
    
    
    def __str__( self ):
        return ansi.FORE_CYAN + str( self.coercer ) + ansi.FORE_RESET + "(" + ansi.FORE_MAGENTA + str( self.info.annotation if self.info else "" ) + ansi.FORE_RESET + ")"


class CoercerCollection:
    """
    Collection of coercers.
    
    Use `register` to register the coercers and `coerce` to coerce strings to values.
    
    See also `get_default_coercer`.
    
    :data coercers: The collection
    :data debug:    Set this to true to print status messages from each coercion by default.
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        self.coercers = []  # List[AbstractCoercer]
        self.__debug_depth: List[_Coercion] = []
        self.debug = False
    
    
    def register( self, *args: AbstractCoercer ):
        """
        Registers a new coercer or coercers.
        
        :param args:    AbstractCoercer(s) to register
        """
        for arg in args:
            self.coercers.append( arg )
    
    
    def __str__( self ):
        return "CoercerCollection with «{}» registered coercers: {}.".format( len( self.coercers ), ", ".join( "«{}»".format( x ) for x in self.coercers ) )
    
    
    def coerce( self, types: object, value: str ):
        """
        Tries all registered coercers to coerce the string into the specified type(s).
        
        :param types:           An acceptable type, sequence of types, annotation, or sequence of annotations.
                                (annotations can be any arbitrary objects that at least one registered AbstractCoercer is
                                 able to understand, e.g. `Union`. They do not need to be derived from `type`.)
                                If a sequence (list or tuple) of is provided, coercion to any of the provided
                                types will be attempted.
                                Note that the exact types and/or annotations accepted depend on which coercers
                                have been registered.
                                 
        :param value:           Source text to coerce.
                                This has different meanings to different coercers.
                                If this starts with `"coerce::"` then debugging information is printed.
                                
        :return:                A value of one of the types in `types`.
        
        :except CoercionError:  Coercion failed. 
        """
        orig_debug = None
        
        if value.startswith( "coerce::" ):
            value = value[len( "coerce::" ):]
            orig_debug = self.debug
            self.debug = True
        
        types: Sequence[type] = array_helper.as_sequence( types )
        
        handlers: List[_Coercion] = []
        
        prefix = ansi.FORE_RED + "𝑪𝑶𝑬𝑹𝑪𝑬 " + ansi.FORE_RESET
        
        if self.debug:
            i = 0
            
            for i, j in enumerate( itertools.chain( [_Coercion( None, None, None )], self.__debug_depth ) ):
                print( prefix + ansi.FORE_RED + ("::::" * (i + 1)) + ansi.FORE_RESET + str( j ) )
            
            type_str = " | ".join( "«{}»".format( x ) for x in types )
            
            if len( self.__debug_depth ) == 0:
                print( prefix + ansi.FORE_RED + ("::::" * (i + 1)) + ansi.FORE_RESET + "===== BEGIN COERCE {} INTO {} =====".format( ansi.FORE_BLUE + value + ansi.FORE_RESET, ansi.FORE_MAGENTA + type_str + ansi.RESET ) )
            else:
                print( prefix + ansi.FORE_RED + ("::::" * (i + 1)) + ansi.FORE_RESET + "DESCENDING INTO {}".format( ansi.FORE_MAGENTA + type_str + ansi.RESET ) )
        
        try:
            if self.debug:
                print( prefix + "ESTABLISHING PRIORITIES:" )
            
            for destination_type in cast( List[type], types ):
                coercion_info = CoercionInfo( AnnotationInspector( destination_type ), self, value )
                
                for coercer in self.coercers:
                    priority = coercer.can_handle( coercion_info )
                    
                    if priority is None:
                        priority = 0
                    elif priority is True:
                        priority = AbstractCoercer.PRIORITY.DEFAULT
                    elif priority is False:
                        priority = 0
                    
                    coercion = _Coercion( priority, coercion_info, coercer )
                    
                    if self.debug:
                        print( prefix + " * PRIORITY " + ansi.FORE_YELLOW + str( coercion.priority ) + ansi.FORE_RESET + " " + str( coercion ) )
                    
                    if priority:
                        handlers.append( coercion )
            
            if not handlers:
                raise CoercionError( "There isn't a handler, in «{}» handlers, that can handle «{}». Details: {}".format( len( self.coercers ), self.__get_type_names( types ), self ) )
            
            exceptions = []
            handlers = [x for x in sorted( handlers, key = lambda y: y.priority )]
            
            if self.debug:
                print( prefix + "READY TO TRY:" )
                
                for index, coercion in enumerate( handlers ):
                    print( prefix + " * {}. {}".format( index, coercion ) )
                
                print( prefix + "TRYING:" )
            
            for index, coercion in enumerate( handlers ):
                try:
                    if not coercion.info._cancelled:
                        if self.debug:
                            print( prefix + " * {}. {}".format( index, coercion ) )
                        
                        self.__debug_depth.append( coercion )
                        result = coercion.coercer.coerce( coercion.info )
                        self.__debug_depth.pop()
                        
                        if self.debug:
                            print( prefix + "     - SUCCESS = {} {}".format( result, type( result ) ) )
                        return result
                except CoercionError as ex:
                    if self.debug:
                        print( prefix + "     - {} FAILURE = {}\n{}".format( "TERMINATING" if ex.cancel else "NORMAL", ex, format_exc() ) )
                    exceptions.append( (coercion, ex) )
                    if ex.cancel:
                        coercion.info._cancelled = True
            
            assert len( exceptions )
            
            self.__failure( types, value, exceptions )
        finally:
            if orig_debug is not None:
                self.debug = orig_debug
    
    
    @staticmethod
    def __get_type_names( destination_types ):
        return "|".join( str( x ) for x in destination_types )
    
    
    def __failure( self, destination_types, source_value, exceptions: List[Tuple[_Coercion, Exception]] ):
        """
        Raises a descriptive `CoercionError` to indicate coercion failure.
        """
        if not self.debug:
            raise CoercionError( "The value «{0}» is not a valid value (expected «{1}»). Use «coerce::{0}» for details.".format( source_value, self.__get_type_names( destination_types ) ) )
        
        message = []
        
        ignore( source_value )
        message.append( 'Cannot coerce into «{}».'.format( self.__get_type_names( destination_types ) ) )
        
        for index, exx in enumerate( exceptions ):
            coercion, ex = exx
            message.append( "  " + str( ex ).replace( "\n", "\n  " ) )
        
        # We do raise `from` because even though we've already included the description because it makes debugging easier
        raise CoercionError( "\n".join( message ) ) from exceptions[0][-1]


class UnionCoercer( AbstractCoercer ):
    """
    **Union** types can be referenced in a format suitable for _either of their member types_.
    
    :remarks:
    This coercer serves one function and is not externally configurable.
    """
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if info.annotation.is_union else None
    
    
    def coerce( self, info: CoercionInfo ):
        params = info.annotation.union_args
        return info.collection.coerce( params, info.source )


class NoneTypeCoercer( AbstractCoercer ):
    """
    The special **None** value may be referenced by the _exact text_ "none" (case insensitive).
    
    :remarks:
    This coercer serves one function and is not externally configurable. 
    """
    
    
    def coerce( self, args: CoercionInfo ):
        if args.source.lower() == "none":
            return None
        
        raise CoercionError( "Only accepting «none» to mean «None»." )
    
    
    def can_handle( self, info: CoercionInfo ):
        return info.annotation.value is type( None )


class AbstractEnumCoercer( AbstractCoercer ):
    """
    Base class for enumerative coercers.
    If the set of options is fixed, only enough character(s) need to be provided to distinguish the enumeration member from the others.
    If the set of options is variable, the user can specify additional options, but the full text must be used to specify an existing option.
    """
    
    
    @abstract
    def can_handle( self, info: CoercionInfo ):
        """
        Same as base class.
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def get_accepts_user_options( self ) -> bool:
        """
        Base class should return if values outside those specified in `list` can be provided.
        If not overridden returns False.
        """
        return False
    
    
    @virtual
    def get_option_name( self, value ):
        """
        Base class should return the name of the option.
        If not overridden returns `str(option)`
        """
        return str( value )
    
    
    @abstract
    def get_options( self, info: CoercionInfo ) -> List[object]:
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def on_user_option( self, info: CoercionInfo ) -> object:
        raise ValueError( "Cannot convert." )
    
    
    def coerce( self, info: CoercionInfo ):
        opts = self.get_options( info )
        
        try:
            return string_helper.find( source = opts,
                                       search = info.source.lower(),
                                       namer = self.get_option_name,
                                       detail = "option",
                                       fuzzy = not self.get_accepts_user_options() )
        except Exception as ex:
            if self.get_accepts_user_options():
                return self.on_user_option( info )
            
            # Halting now to prevent fallback to `str`.
            raise CoercionError( "«" + info.source + "» is not a valid option in: " + ", ".join( "«{}»".format( self.get_option_name( x ) ) for x in opts ), cancel = True ) from ex


class EnumCoercer( AbstractEnumCoercer ):
    """
    **Enumeration members** may be referenced by their _names_ (case insensitive).
    Only enough character(s) need to be provided to distinguish the enumeration member from the others.
    
    :remarks:
    This coercer serves one function and is not externally configurable.
    """
    
    
    def get_options( self, args: CoercionInfo ) -> List[object]:
        return [x for x in cast( Type[Enum], args.annotation.value ) if isinstance( x, args.annotation.value )]
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if (info.annotation.is_directly_below( Enum )) else None
    
    
    def get_option_name( self, value ):
        return value.name.lower()


class BoolCoercer( AbstractCoercer ):
    """
    **Boolean** values may be specified as _text_: "true"/"false", "yes"/"no", "y"/"n", "t"/"f" or "1"/"0". Case insensitive.
    
    :remarks:
    This coercer serves one function and is not externally configurable.
    """
    
    
    def coerce( self, args: CoercionInfo ):
        try:
            return string_helper.to_bool( args.source )
        except Exception as ex:
            # Halting now to prevent fallback to True.
            raise CoercionError( "«" + args.source + "» is not a valid boolean in: «true», «false», «yes», «no», «t», «f», «y», «n», «1», «0»", cancel = True ) from ex
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if (info.annotation.value is bool) else None


class ListCoercer( AbstractCoercer ):
    """
    **Lists** may be specified as a _comma delimited string_ (do not add extra spaces between list items).
    
    :remarks:
    This coercer serves one function and is not externally configurable.
    """
    
    
    def coerce( self, args: CoercionInfo ):
        # noinspection PyUnresolvedReferences
        list_type_ = args.annotation.generic_list_type
        elements = args.source.split( "," )
        result = list()
        
        for x in elements:
            result.append( args.collection.coerce( list_type_, x ) )
        
        return result
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if info.annotation.is_generic_list else None


class PasswordCoercer( AbstractCoercer ):
    """
    **Passwords** may be specified by _an asterisk_ "*", which causes the terminal to prompt for the password safely.
    
    :remarks:
    This coercer serves one function and is not externally configurable.
    """
    
    
    def coerce( self, info: CoercionInfo ):
        if info.source in ("*", "prompt"):
            print( "Prompting for password." )
            import getpass
            value = getpass.getpass( "(PLEASE ENTER PASSWORD)" )
            
            if not value:
                raise CoercionError( "No password provided." )
            
            return info.annotation.value( value )
        else:
            return info.annotation.value( info.source )
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if (info.annotation.is_directly_below( Password )) else None


class ObjectCoercer( AbstractCoercer ):
    """
    **Objects** may be provided _as string objects_.
    
    :remarks:
    This coercer serves one function and is not externally configurable.
    """
    
    
    def coerce( self, args: CoercionInfo ):
        return args.source
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.INBUILT if (info.annotation.value is object) else None


class FallbackCoercer( AbstractCoercer ):
    """
    **Standard types** may be referenced as _any acceptable value_ to their Python constructor, e.g. text for strings ("hello world"), numbers for integers ("123") and floats ("1.23").
    
    :remarks:
    This coercer serves one function and is not externally configurable.
    """
    
    
    def can_handle( self, info: CoercionInfo ):
        return self.PRIORITY.FALLBACK
    
    
    def coerce( self, args: CoercionInfo ):
        try:
            return args.annotation.value( args.source )
        except Exception as ex:
            raise CoercionError( "Cannot coerce the value via the constructor «{}».".format( args.annotation ) ) from ex


__default_coercer = None


def get_default_coercer() -> CoercerCollection:
    global __default_coercer
    
    if __default_coercer is None:
        __default_coercer = CoercerCollection()
        __default_coercer.register( PasswordCoercer() )
        __default_coercer.register( UnionCoercer() )
        __default_coercer.register( NoneTypeCoercer() )
        __default_coercer.register( EnumCoercer() )
        __default_coercer.register( BoolCoercer() )
        __default_coercer.register( ListCoercer() )
        __default_coercer.register( ObjectCoercer() )
        __default_coercer.register( FallbackCoercer() )
    
    return __default_coercer


def register( *args: AbstractCoercer ):
    return get_default_coercer().register( *args )
