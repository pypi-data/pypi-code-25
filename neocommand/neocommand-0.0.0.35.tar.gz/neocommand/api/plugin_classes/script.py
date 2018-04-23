"""
Contains the `ScriptPlugin` class, an extension of the `intermake` package's Plugin that represents re-usable Cypher scripts.

The `ScriptPlugin` itself is ideally constructed through the `Script` convenience function.
"""
import inspect
from typing import Dict, List, Optional

from intermake import EThread, MCMD, Plugin, VisibilityClass
from mhelper import AnnotationInspector, MAnnotationFactory, array_helper, override, sealed, string_helper, NOT_PROVIDED
from mhelper.reflection_helper import FnArg, ArgsKwargs, FnArgValueCollection
from neocommand.endpoints.bases import AbstractDestination


__author__ = "Martin Rusilowicz"


# HDbParam - used to denote arguments in ScriptPlugins that are passed as database arguments (i.e. direct to Neo4j).
# Replaces {xyz} in the script. The better option but Neo4j doesn't support this in all cases.
HDbParam = MAnnotationFactory( "DBParam" )

# HScriptParam - used to denote arguments in ScriptPlugins that are passed as a text replacement in the script.
# Replaces <XYZ> in the script.
HScriptParam = MAnnotationFactory( "HScriptParam" )


TScriptTypes = "Union[ Type[ HDbParam ], Type[ HScriptParam ] ]"
TScriptParam = "Union[ TScriptTypes, Tuple[ TScriptTypes, object ] ]"


# noinspection PyUnusedLocal
def Script( *,
            cypher: str,
            name: str = None,
            description: Optional[str] = None,
            timeout = None,
            retries = None,
            visibility = None,
            arguments: Dict[str, TScriptParam] = None ) -> "ScriptPlugin":
    """
     Creates a ScriptPlugin. All parameters apart from _script are optional.
     The parameters begin with underscores to separate them from the script parameters - kwargs.
     
     Parameters and replacements should be passed as tuples of types and defaults, or just types.

        :param visibility:         Inherited 
        :param cypher:             The script template itself (str, use "<XXX> for arguments - see kwargs)
        :param name:               Name of the script (str, None)
        :param description:        Description of what the script does (str, None)
        :param timeout:            Timeout period for query (0 for no timeout, default is 0)
        :param retries:            Number of retries after query timeout (0 for no reties, default is infinite).
        :param arguments:          Script arguments.
    """
    
    # Description
    description = inspect.cleandoc( description ) if description else ""
    
    cypher = string_helper.strip_lines( cypher )
    description += "\n\n" + cypher
    
    # Args
    args = []
    
    if arguments:
        for arg_name, arg_info in arguments.items():
            if arg_name in ("timeout", "retries"):
                raise ValueError( "Legacy script parameter. Please remove." )
            
            if arg_info is not None:
                arg_info = array_helper.as_sequence( arg_info )
                arg_annotation = AnnotationInspector( arg_info[0] )
                arg_default = arg_info[1] if len( arg_info ) > 1 else NOT_PROVIDED
                arg_description = arg_info[2] if len( arg_info ) > 2 else "Script parameter"
                
                if not arg_annotation.is_mannotation_of( HDbParam ) \
                        and not arg_annotation.is_mannotation_of( HScriptParam ):
                    raise ValueError( "The type of argument «{}» on the script «{}» is a «{}», but it should be an <HDbParam> or <HScriptParam>.".format( arg_name, name or cypher, arg_annotation ) )
                
                args.append( FnArg( arg_name, arg_annotation.value, arg_default, arg_description ) )
    
    # Special arguments for scripts:
    if timeout is None:
        timeout = 0
    
    if retries is None:
        retries = 1000
    
    plugin = ScriptPlugin( cypher = cypher,
                           name = name,
                           description = description,
                           args = args,
                           visibility = visibility,
                           timeout = timeout,
                           retries = retries )
    
    return plugin


SCRIPT_VISIBILITY = VisibilityClass( name = "scripts",
                                     is_visible = False,
                                     comment = "Cypher scriptlets" )


class ScriptPlugin( Plugin ):
    """
    Wraps text with replaceable parameters up with some error checking

    These "parameters" are just text and should represent constants as far as the database is concerned.
    They should not be confused with, or used as a substitute for, database query parameters.
    """
    __ARBITRARY_COUNTER = 1
    
    def __init__( self,
                  cypher: str,
                  name: str,
                  description: str,
                  args: List[FnArg],
                  visibility: Optional[VisibilityClass],
                  timeout: int,
                  retries: int ):
        """
        CONSTRUCTOR
        See Script() for argument descriptions.
        """
        from neocommand.endpoints.standard import ECHOING_ENDPOINT
        
        assert cypher is not None, "A script plugin «{0}» needs some code.".format( name )
        
        arg_list = { }
        
        if not name:
            name = "untitled.script.{}".format( self.__ARBITRARY_COUNTER )
            self.__ARBITRARY_COUNTER += 1
            
            if description is None:
                description = "Internal script not intended for user access."
        
        super().__init__( names = [ name ],
                          description = description,
                          threading = EThread.SINGLE,
                          visibility = visibility )
        
        # Arguments
        for x in args:
            super()._add_argument( x )
            arg_list[x.name] = x
        
        # Suck in arguments from arguments that are themselves Scripts
        to_add = []
        
        for arg in self.args:
            dv = arg.default
            
            if isinstance( dv, ScriptPlugin ):
                for v in dv.args:  # type: FnArg
                    if not v.name in arg_list:
                        to_add.append( v )
        
        for v in to_add:
            self._add_argument( v )
            arg_list[v.name] = v

        from neocommand.endpoints.standard import DbEndpoint
        self.__arg_database = super()._add_arg( "database", Optional[DbEndpoint], None, "Database to use. If this is `None` a reasonable default will be assumed." )
        self.__arg_output = super()._add_arg( "output", AbstractDestination, ECHOING_ENDPOINT, "Where to send received data." )
        self.__arg_timeout = super()._add_arg( "timeout", int, timeout, "Parameter available to all scripts. Query timeout in seconds, use zero for no timeout." )
        self.__arg_retries = super()._add_arg( "retries", int, retries, "Parameter available to all scripts. Number of retries after timeouts before the query is considered a failure" )
        self.__arg_quiet = super()._add_arg( "quiet", bool, False, "Don't display results in terminal." )
        
        self._script = cypher
        
        if "limit" in arg_list:
            self.__arg_limit = arg_list["limit"]
        
        # MODE_BATCH scripts are really just MODE_ITERATIVE scripts
        # but we must auto-create some additional details
        
        # Extra args
        self.arg_dump = super()._add_arg( "_dump", bool, False, "Dump the script's code to standard output instead of running it." )
    
    
    def new_default_args( self,
                          **kwargs ) -> List[FnArg]:
        new_args = []
        
        for arg in self.args:
            if arg.name in kwargs:
                default = kwargs[arg.name]
            else:
                default = arg.default
            
            new_args.append( FnArg( arg.name, arg.annotation.value, default, arg.description ) )
        
        return new_args
    
    
    @override
    @sealed
    def on_run( self ) -> Optional[object]:
        """
        IMPLEMENTATION
        The meaty bit
        """
        
        #
        # GET ARGUMENTS
        #
        arg_dump = MCMD.args.get_value( self.arg_dump)
        arg_database = MCMD.args.get_value( self.__arg_database)
        arg_timeout = MCMD.args.get_value( self.__arg_timeout)
        arg_retries = MCMD.args.get_value( self.__arg_retries)
        arg_output = MCMD.args.get_value( self.__arg_output)
        arg_quiet = MCMD.args.get_value( self.__arg_quiet)
        
        if arg_database is None:
            from neocommand.core.core import CORE
            arg_database = CORE.endpoint_manager.get_database_endpoint()
        
        #
        # GET CODE
        #
        cypher = self.create( MCMD.args )
        
        cypher_params = { }
        
        for arg, value in MCMD.args.items():
            if arg.annotation.is_mannotation_of( HDbParam ):
                cypher_params[arg.name] = value
        
        #
        # SPECIAL CASE FOR CYPHER DUMP
        #
        if arg_dump:
            MCMD.print( cypher )
            
            for k, v in cypher_params.items():
                MCMD.print( "{} = {}".format( k, v ) )
            
            return None
        
        #
        # RUN THE SCRIPT!
        #
        with arg_database.get_database() as db:
            result = db.run_cypher( title = self.name,
                                    cypher = cypher,
                                    parameters = cypher_params,
                                    time_out = arg_timeout,
                                    retry_count = arg_retries,
                                    output = arg_output )
            
            if not arg_quiet:
                MCMD.information( result )
            
            return result
    
    
    def plain_text( self ):
        return self._script
    
    
    def check_holds_true( self, condition, message = "" ) -> None:
        if not condition:
            raise ValueError( "There is an error in the script \"" + self.name + "\". " + message + "." )
    
    
    @property
    def estimator( self ) -> "Optional[Script]":
        """

        :return:
        """
        return self._estimator
    
    
    def create( self, 
                args: Optional[FnArgValueCollection] = None,
                ignore_missing: bool = False ) -> str:
        """
        Generates the text from this script object, parameters may be specified at this time
        Any parameters left unfilled will cause an error!
        """
        if args is None:
            args = FnArgValueCollection( self.args, ArgsKwargs(  ) )  # Just use the defaults
        
        return self._create_from( self._script, args, ignore_missing )
    
    
    @staticmethod
    def _create_from( statement : str,
                      args: FnArgValueCollection, 
                      ignore_missing: bool ) -> str:
        """
        Logic behind create().
        """
        
        for arg, value in args.items():
            
            key = "<" + arg.name.upper() + ">"
            
            # Assert parameter exists
            if value is NOT_PROVIDED:
                if ignore_missing:
                    value = "{????}"
                else:
                    raise ValueError( "The parameter «{0}» of type «{1}» has not been provided.".format( arg.name, arg.annotation ) )
            
            # Scripts can reference other scripts
            if isinstance( value, ScriptPlugin ):
                new_dict = { }
                
                for arg2, value2 in args.items():
                    if arg2.name in [x.name for x in value.args]:
                        new_dict[arg2.name] = value2
                
                value = value.create( args, ignore_missing )  # parameters get passed along
            
            statement = statement.replace( key, str( value ) )
        
        return statement
