import warnings
from os import path
from typing import Optional, Dict, Iterator, List, Tuple, Union
from uuid import uuid4

import keyring as keyring_
from intermake.engine.environment import MCMD, MENV
from intermake.visualisables.visualisable import UiInfo, EColour, IVisualisable
from keyring.errors import PasswordDeleteError
from mhelper import NotSupportedError, ManagedWith, array_helper, Filename, io_helper, override, file_helper
from neocommand.helpers.resolver import EntityResolver
from neocommand.core import constants
from neocommand.data.entities import Edge, Node, IEntity
from neocommand.endpoints.bases import AbstractMasterOrigin, AddFailedError, AbstractOrigin, AbstractListBackedEndpoint, AbstractFileEndpoint, AbstractDestination
from neocommand.helpers.neo_csv_helper import NeoCsvMultiWriter, NeoCsvFilename, NeoCsvReader
from neocommand.helpers.resolver import EdgeNodeDict
from neocommand.core.annotations import TNodeLabel, TEdgeLabel, TNodeUid, TNodeProperty, TDriverName


_DbManager = "neocommand.database.database_manager.DbManager"


class __DbEndpointScriptsClass:
    def __init__( self ) -> None:
        from neocommand.api.plugin_classes.script import HScriptParam, HDbParam, Script
        
        self.PROPERTY_LOOKUP_UID = Script( cypher = """
                                                    MATCH (a:<LABEL> {uid: {uid}})
                                                    RETURN a.`<PROPERTY>`
                                                    """,
                                           timeout = constants.TIME_SHORT_TIMEOUT,
                                           arguments = { "label"   : HScriptParam[TNodeLabel],
                                                         "uid"     : HDbParam[TNodeUid],
                                                         "property": HScriptParam[TNodeProperty] } )
        
        self.PROPERTY_LOOKUP_IID = Script( cypher = """
                                            MATCH (a) WHERE ID(a) = {iid}
                                            RETURN a.`<PROPERTY>`
                                            """,
                                           arguments = { "iid"     : HDbParam[TNodeUid],
                                                         "property": HScriptParam[TNodeProperty] },
                                           timeout = constants.TIME_SHORT_TIMEOUT )
        
        self.NODE_LOOKUP_UID = Script( cypher = """
                                        MATCH (n:<LABEL> { uid:{uid} })
                                        RETURN n
                                     """,
                                       arguments = { "label": HScriptParam[TNodeLabel],
                                                     "uid"  : HDbParam[TNodeUid] }, )
        
        self.NODE_LOOKUP_IID = Script( cypher = """
                                        MATCH (n) WHERE ID(n) = {id}
                                        RETURN n
                                     """,
                                       arguments = { "id": HDbParam[int] }, )
        
        self.EDGE_LOOKUP = Script( cypher = """
                                            MATCH (n:<START_LABEL> { uid:{start_uid} })-[r:<LABEL>]->(m:<END_LABEL> { uid:{end_uid} })
                                            RETURN r
                                            """,
                                   arguments = { "start_label": HScriptParam[TNodeLabel],
                                                 "end_label"  : HScriptParam[TNodeLabel],
                                                 "label"      : HScriptParam[TEdgeLabel],
                                                 "start_uid"  : HDbParam[TNodeUid],
                                                 "end_uid"    : HDbParam[TNodeUid] } )
        
        self.EDGE_LOOKUP_NODE_ID = Script( cypher = """
                                            MATCH (n)-[r]->(m) WHERE ID(n) = {start_id} AND ID (m) = {end_id}
                                            RETURN r
                                         """,
                                           arguments = { "start_id": HDbParam[int],
                                                         "end_id"  : HDbParam[int] } )
        
        self.EDGE_ID_LOOKUP = Script( cypher = """
                                               MATCH p = (n)-[r]->(m) WHERE ID(r) = {id}
                                               RETURN p
                                               """,
                                      arguments = { "id": HDbParam[int] } )


__db_endpoint_scripts = None


def _db_endpoint_scripts() -> __DbEndpointScriptsClass:
    global __db_endpoint_scripts
    
    if __db_endpoint_scripts is None:
        __db_endpoint_scripts = __DbEndpointScriptsClass()
    
    return __db_endpoint_scripts


class NullEndpoint( AbstractDestination ):
    """
    A write-only endpoint that doesn't write the data anywhere.
    """
    FIXED_NAME = "null"
    
    
    def on_get_name( self ) -> str:
        return self.FIXED_NAME
    
    
    def on_endpoint_set_name( self, value: str ):
        raise ValueError( "Cannot change the name of a system endpoint." )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = "null",
                       doc = "AbstractDestination that doesn't send anywhere.",
                       type_name = "NULL_EP",
                       value = "Maps I/O to null",
                       colour = self.ENDPOINT_COLOUR,
                       icon = self.ENDPOINT_ICON )
    
    
    def __str__( self ) -> str:
        return "NULL_EP"
    
    
    def on_endpoint_add_data( self, data: object ):
        pass  # by intent
    
    
    def on_endpoint_create_folder( self, name: str ) -> "AbstractDestination":
        pass  # by intent
    
    
    def on_endpoint_add_edge( self, edge: Edge ):
        pass  # by intent
    
    
    def on_endpoint_add_node( self, node: Node ):
        pass  # by intent
    
    
    def on_endpoint_flush( self ) -> None:
        pass
    
    
    def __bool__( self ) -> bool:
        return False


NULL_ENDPOINT = NullEndpoint()


class DbEndpoint( AbstractMasterOrigin, AbstractDestination ):
    """
    A read/write endpoint that reads and writes data to/from the database
    
    For obvious reasons, attempts to read the entire database will result in an error.
    """
    
    
    class _ConnectionInfo:
        """
        Holds the connection information as a single marshallable object.
        """
        
        
        def __init__( self, name: str, driver: TDriverName, remote_address: str, user_name: str, directory: Optional[str], is_unix: Optional[bool], port: str ):
            self.name = name
            self.driver = driver
            self.remote_address = remote_address
            self.user_name = user_name
            self.directory = directory
            self.is_unix = is_unix
            self.port = port
        
        
        def get_directory( self ) -> str:
            if self.directory:
                return self.directory
            
            raise NotSupportedError( "Cannot obtain the Neo4j directory because the directory was not specified when the DbEndpoint was created." )
        
        
        def get_binary_directory( self ) -> str:
            return path.join( self.get_directory(), "bin" )
        
        
        def get_import_directory( self ) -> str:
            return path.join( self.get_directory(), "import" )
        
        
        def get_is_unix( self ) -> bool:
            if self.is_unix is not None:
                return self.is_unix
            
            raise NotSupportedError( "Cannot determine if Neo4j is running under Windows or Unix because that was not specified when the DbEndpoint was created." )
    
    
    def __getstate__( self ) -> Dict[str, object]:
        result = { "connection_info": self.__connection_info,
                   "password_key"   : self.__password_key }
        
        if not self.__password_key:
            result["password"] = self.__password
        
        return result
    
    
    def __setstate__( self, state: Dict[str, object] ) -> None:
        self.__connection_info = state["connection_info"]
        self.__password_key = state["password_key"]
        
        if self.__password_key:
            self.__password = keyring_.get_password( constants.KEYRING_NAME, self.__get_password_key() )
        else:
            self.__password = state["password"]
        
        self.__connections = []
        self.__used_connections = []
    
    
    def __get_password_key( self ) -> str:
        return "DbEndpoint:{}@{}+{}".format( self.__connection_info.user_name, self.__connection_info.remote_address, self.__password_key )
    
    
    def __init__( self,
                  *,
                  name: str,
                  driver: TDriverName,
                  remote_address: str,
                  user_name: str,
                  password: str,
                  directory: Optional[str],
                  is_unix: Optional[bool],
                  port: str,
                  keyring: bool ):
        super().__init__()
        
        self.__connection_info = self._ConnectionInfo( name, driver, remote_address, user_name, directory, is_unix, port )
        self.__password = password
        self.__password_key = str( uuid4() ) if keyring else None
        self.__connections = []
        self.__used_connections = []
        
        if keyring:
            keyring_.set_password( constants.KEYRING_NAME, self.__get_password_key(), self.__password )
            MCMD.progress( "Endpoint created. I have added the password to your system keyring." )
    
    
    def on_endpoint_deleted( self ) -> None:
        if self.__password_key:
            try:
                keyring_.delete_password( constants.KEYRING_NAME, self.__get_password_key() )
                MCMD.progress( "Endpoint deleted. I have removed the password from your system keyring." )
            except PasswordDeleteError as ex:
                warnings.warn( str( ex ), UserWarning )
    
    
    @property
    def connection_info( self ) -> "DbEndpoint._ConnectionInfo":
        return self.__connection_info
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.__connection_info.name,
                       doc = str( self.__doc__ ),
                       type_name = "DB_EP",
                       value = str( self ),
                       colour = self.ENDPOINT_COLOUR,
                       icon = self.ENDPOINT_ICON,
                       extra = { "user_name"       : self.__connection_info.user_name,
                                 "remote_address"  : self.__connection_info.remote_address,
                                 "driver"          : self.__connection_info.driver,
                                 "directory"       : self.__connection_info.directory,
                                 "is_unix"         : self.__connection_info.is_unix,
                                 "password"        : "********" if (self.__password_key and self.__password) else self.__password,
                                 "connections"     : len( self.__connections ) + len( self.__used_connections ),
                                 "connections_idle": len( self.__connections ),
                                 "connections_used": len( self.__used_connections ) } )
    
    
    def __repr__( self ) -> str:
        return "{}@{}".format( self.__connection_info.user_name, self.__connection_info.remote_address )
    
    
    def __acquire_manager( self ) -> _DbManager:
        if not self.__connections:
            from neocommand.core.database_manager import DbManager
            self.__connections.append( DbManager( self.__connection_info.driver, self.__connection_info.remote_address, self.__connection_info.user_name, self.__password, self.__connection_info.port ) )
        
        result = self.__connections.pop()
        self.__used_connections.append( result )
        return result
    
    
    def __release_manager( self, manager: _DbManager ) -> None:
        self.__used_connections.remove( manager )
        self.__connections.append( manager )
    
    
    def get_database( self ) -> ManagedWith:
        return ManagedWith( on_get_target = self.__acquire_manager, on_exit = self.__release_manager )
    
    
    def origin_get_edge_by_iid( self, iid: int ) -> Edge:
        ep = MemoryEndpoint()
        _db_endpoint_scripts().EDGE_ID_LOOKUP( id = iid,
                                               database = self,
                                               output = ep,
                                               quiet = True )
        
        return ep.only_child( Edge )
    
    
    def origin_get_edge_by_node_uids( self, label: str, start_label: str, end_label: str, start_uid: str, end_uid: str ) -> Edge:
        ep = MemoryEndpoint()
        _db_endpoint_scripts().EDGE_LOOKUP( label = label,
                                            start_label = start_label,
                                            end_label = end_label,
                                            start_uid = start_uid,
                                            end_uid = end_uid,
                                            database = self,
                                            output = ep,
                                            quiet = True )
        
        return ep.only_child( Edge )
    
    
    def origin_get_edge_by_node_iids( self, start_iid: int, end_iid: int ) -> Edge:
        ep = MemoryEndpoint()
        _db_endpoint_scripts().EDGE_LOOKUP_NODE_ID( start_id = start_iid,
                                                    end_id = end_iid,
                                                    database = self,
                                                    output = ep,
                                                    quiet = True )
        
        return ep.only_child( Edge )
    
    
    def origin_get_all( self ) -> Iterator[IEntity]:
        raise NotSupportedError( "Refusing to retrieve the entire database («{}»). Perhaps you meant to operate on a subset of the database?".format( self ) )
    
    
    def origin_get_all_nodes_property( self, label: str, property: str ) -> List[Tuple[str, object]]:
        text = "MATCH (n:`" + label + "`) RETURN n.`uid`, n.`" + property + "`"
        
        with self.get_database() as db:
            result = MemoryEndpoint()
            db.run_cypher( "Get properties", text, result )
            result_list = array_helper.deinterleave_as_list( result.contents )  # type: List[Tuple[ str, object ] ]
            return result_list
    
    
    def origin_get_node_property_by_uid( self, label: str, uid: str, property: str ):
        ep = MemoryEndpoint()
        _db_endpoint_scripts().PROPERTY_LOOKUP_UID( label = label,
                                                    uid = uid,
                                                    property = property,
                                                    database = self,
                                                    output = ep,
                                                    quiet = True )
        return ep.only_child( object )
    
    
    def origin_get_node_property_by_iid( self, iid: int, property: str ):
        ep = MemoryEndpoint()
        _db_endpoint_scripts().PROPERTY_LOOKUP_IID( iid = iid,
                                                    property = property,
                                                    database = self,
                                                    output = ep,
                                                    quiet = True )
        return ep.only_child( object )
    
    
    def origin_get_node_by_uid( self, label: str, uid: str ):
        assert label
        assert uid
        
        ep = MemoryEndpoint()
        _db_endpoint_scripts().NODE_LOOKUP_UID( label = label,
                                                uid = uid,
                                                database = self,
                                                output = ep,
                                                quiet = True )
        return ep.only_child( Node )
    
    
    def origin_get_node_by_iid( self, iid: int ):
        ep = MemoryEndpoint()
        _db_endpoint_scripts().NODE_LOOKUP_IID( id = iid,
                                                database = self,
                                                output = ep,
                                                quiet = True )
        
        return ep.only_child( Node )
    
    
    def on_endpoint_set_name( self, value: str ):
        self.__connection_info.name = value
    
    
    def on_get_name( self ) -> str:
        return self.__connection_info.name
    
    
    def on_endpoint_create_folder( self, _: str ) -> "AbstractDestination":
        return self
    
    
    def on_endpoint_add_data( self, data: object ):
        warnings.warn( "This endpoint «{}» does not support the adding of arbitrary (non-node/edge) data «{}». This action has been ignored.".format( self, data ) )
    
    
    def on_endpoint_add_edge( self, edge: Edge ):
        args = []
        for k in edge.properties.keys():
            args.append( "r.`" + k + "` = {" + k + "}" )
        
        args = ",".join( args )
        
        if args:
            args = " SET " + args
        
        text = "MATCH (n:`" + edge.start.label + "` {uid:{start_uid}}), (m:`" + edge.end.label + "` {uid:{end_uid}}) MERGE (n)-[r:`" + edge.label + "`]->(m)" + args
        
        # noinspection PyTypeChecker
        parameters = dict( edge.properties.items() )
        parameters["start_uid"] = edge.start.uid
        parameters["end_uid"] = edge.end.uid
        
        with MCMD.host.database() as db:
            stats = None
            
            try:
                stats = db.run_cypher( "Create edge", text, MCMD, parameters, output = NULL_ENDPOINT )
                
                if stats.nodes_created != 0:
                    raise AddFailedError( "stats.nodes_created is {0} (expected 0)".format( stats.nodes_created ) )
                    
                    # if stats.relationships_created != 1:
                    #     raise AddFailedError( "stats.relationships_created is {0} (expected 1)".format( stats.relationships_created ) )
            
            except Exception as ex:
                raise AddFailedError( "Failed to add the edge due to the error «{0}». Properties: ({1} {2})-[{3}]>({4} {5}) {6}. Stats: {7}".format( ex, edge.start.label, edge.start.uid, edge.label, edge.end.label, edge.end.uid, edge.properties, stats ) ) from ex
    
    
    def on_endpoint_flush( self ) -> None:
        pass
    
    
    def on_endpoint_add_node( self, node: Node ):
        args = []
        # noinspection PyTypeChecker
        parameters = dict( node.properties.items() )
        parameters["uid"] = node.uid
        
        for k in parameters.keys():
            args.append( "n.`" + k + "` = {" + k + "}" )
        
        args = ",".join( args )
        
        if args:
            args = " SET " + args
        
        text = "MERGE (n:`" + node.label + "` {uid: {uid}})" + args
        
        with self.get_database() as db:
            stats = None
            
            try:
                stats = db.run_cypher( title = "Create node",
                                       cypher = text,
                                       parameters = parameters,
                                       output = NULL_ENDPOINT )
                
                # if stats.nodes_created != 1:
                #     raise AddFailedError( "stats.nodes_created is {0} (expected 1)".format( stats.nodes_created ) )
            except Exception as ex:
                raise AddFailedError( "Failed to add a database node due to the error «{0}». Label: «{1}»\nProperties: «{2}»\nStats: {3}".format( ex, node.label, node.properties, stats ) ) from ex


class PickleEndpoint( AbstractListBackedEndpoint ):
    """
    An endpoint, as a disk pickle.
    """
    # noinspection SpellCheckingInspection
    _EXT_ENDPOINT_PICKLE = ".eppickle"
    
    
    def __init__( self, name: str, file_name: Filename[_EXT_ENDPOINT_PICKLE], *, comment = None ):
        super().__init__( name, comment )
        self.__file_name = file_name
        self.__contents = None
    
    
    @property
    def contents( self ) -> List[Optional[object]]:
        if self.__contents is None:
            if path.isfile( self.__file_name ):
                try:
                    self.__contents = io_helper.load_binary( self.__file_name, type_ = list )
                    assert isinstance( self.__contents, list )
                except Exception as ex:
                    raise ValueError( "Failed to recover the PickleEndpoint disk-list from «{0}». The internal error is «{1}: {2}». If this is causing problems, you may have to delete the endpoint and recreate it.".format( self.__file_name, type( ex ).__name__, ex ) )
            else:
                self.__contents = []
        
        return self.__contents
    
    
    def on_endpoint_flush( self ) -> None:
        io_helper.save_binary( self.__file_name, self.__contents )
    
    
    def visualisable_info( self ) -> UiInfo:
        value_str = ("{} items".format( len( self.__contents ) )) if (self.__contents is not None) else "Not yet loaded"
        
        return UiInfo( name = self.endpoint_name,
                       doc = "Endpoint backed to pickle" + ((": " + self.comment) if self.comment else ""),
                       type_name = "RAM_EP",
                       value = value_str,
                       colour = EColour.YELLOW,
                       icon = "folder",
                       extra = { "file": self.__file_name } )
    
    
    @override
    def __getstate__( self ) -> Dict[str, object]:
        return { "name"     : self.endpoint_name,
                 "file_name": self.__file_name }
    
    
    @override
    def __setstate__( self, state: Dict[str, object] ) -> None:
        self.endpoint_name = state["name"]
        self.__file_name = state["name"]
        self.__contents = None


class MemoryEndpoint( AbstractListBackedEndpoint ):
    """
    An endpoint, in local system memory.
    Can be pickled to disk.
    """
    
    
    def on_endpoint_flush( self ) -> None:
        pass
    
    
    def __init__( self, name: Optional[str] = None, *, comment = None ) -> None:
        super().__init__( name, comment )
        self.__contents = _SafeList()
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.endpoint_name,
                       doc = "Endpoint in local memory" + ((": " + self.comment) if self.comment else ""),
                       type_name = "RAM_EP",
                       value = "{} items".format( len( self.contents ) ),
                       colour = EColour.YELLOW, icon = "folder" )
    
    
    @property
    def contents( self ) -> List[Optional[object]]:
        return self.__contents
    
    
    def __iter__( self ):
        return iter( self.__contents )
    
    
    def recurse( self, *, resolve: Union[bool, "EntityResolver"] = False ):
        """
        Recurses over the entities of the endpoint, and any sub-endpoints

            
        :param resolve: Resolver to pass the results through.
                        `None` to use the default resolver.
                        Warning: `None` is for API use only and should not be used internally.
                                 If there is no default resolver an exception will be raised!
        """
        if resolve:
            if resolve is True:
                resolve = EntityResolver()
            
            resolve = resolve.acquire()
            yield from (resolve.resolve_entity( x ) for x in self.recurse())
            return
        
        for x in self.contents:
            if isinstance( x, MemoryEndpoint ):
                yield from x.recurse()
            else:
                yield x


class _SafeList( list ):
    SAFE_TYPES = (int, str, float, bool, list, tuple, Node, Edge, MemoryEndpoint)
    
    
    def append( self, item: object ) -> None:
        if not type( item ) in self.SAFE_TYPES:
            raise ValueError( "Attempt to add an item «{}» of type «{}» to a SafeList, but the SafeList doesn't expect such items." )
        
        super().append( item )


class NeoCsvFolderEndpoint( AbstractDestination, AbstractOrigin ):
    """
    Represents a single folder and the actions to perform upon it
    
    When used as a function annotation to a Plugin this denotes the parcel may or may not exist because the default `create` value on `__init__` is `None`.
    """
    
    
    def on_get_name( self ) -> str:
        return self.__name
    
    
    def on_endpoint_set_name( self, value: str ) -> None:
        self.__name = value
    
    
    # region Unique
    
    
    def remove_folder_from_disk( self ) -> None:
        """
        Remove the folder from the disk
        """
        file_helper.recycle_file( self.__path )
    
    
    def __init__( self, name: str, path: str ):
        """
        CONSTRUCTOR
        :param name: Name or path of parcel 
        """
        super().__init__()
        self.__name = name
        self.__path = path
        self.__writer = NeoCsvMultiWriter( self.full_path() )
        file_helper.create_directory( self.__path )
    
    
    def validate( self ) -> None:
        """
        Raises an error of the parcel directory doesn't exist
        """
        if not path.isdir( self.full_path() ):
            raise FileNotFoundError( "The parcel «{0}» does not exist".format( self ) )
    
    
    def get_file( self, name ) -> str:
        """
        Obtains the full filename of the file called `name`
        """
        return path.join( self.full_path(), name )
    
    
    def iterate_contents( self ) -> Iterator[NeoCsvFilename]:
        if not self.exists():
            return
        
        for file_name in file_helper.list_dir( self.full_path(), constants.EXT_B42CSV, False ):
            try:
                yield NeoCsvFilename.construct_from_file( file_name )
            except:
                pass
    
    
    def exists( self ) -> bool:
        return path.isdir( self.full_path() )
    
    
    def full_path( self ) -> str:
        return self.__path
    
    
    # endregion
    
    # region object
    
    @override
    def __str__( self ) -> str:
        return file_helper.get_filename( self.__path )
    
    
    @override
    def __len__( self ) -> int:
        return len( list( self.iterate_contents() ) )
    
    
    # endregion
    
    # region IVisualisable
    
    
    @override
    def visualisable_info( self ) -> UiInfo:
        if self.exists():
            value_text = "Maps I/O to folder on disk ({} items)".format( len( self ) )
        else:
            value_text = "Maps I/O to folder on disk (**MISSING**)"
        
        return UiInfo( name = str( self ),
                       doc = "NeoCsvFolderEndpoint at «{}»".format( self.full_path() ),
                       type_name = "NEOCSV_EP",
                       value = value_text,
                       colour = self.FILE_ENDPOINT_COLOUR,
                       icon = self.FILE_ENDPOINT_ICON,
                       extra_named = self.iterate_contents,
                       extra = { "directory": file_helper.get_directory( self.__path ),
                                 "file_name": file_helper.get_filename( self.__path ),
                                 "full_path": self.full_path() } )
    
    
    # endregion
    
    # region AbstractOrigin
    
    @override
    def origin_get_all( self ) -> Iterator[IEntity]:
        for file in self.iterate_contents():
            reader = NeoCsvReader( file )
            
            is_edge = file.is_edge
            
            if is_edge:
                for line in reader:
                    start = Node( label = file.start_label, uid = line[constants.NEO4J_START_ID_SUFFIX], iid = None, name = None, comment = None, properties = None )
                    end = Node( label = file.end_label, uid = line[constants.NEO4J_END_ID_SUFFIX], iid = None, name = None, comment = None, properties = None )
                    data = { }
                    
                    for key, value in line.items():
                        if key not in (constants.NEO4J_START_ID_SUFFIX, constants.NEO4J_END_ID_SUFFIX):
                            data[key] = value
                    
                    yield Edge( name = None, comment = None, iid = None, label = file.label, start = start, end = end, properties = data )
    
    
    @override
    def origin_get_all_nodes_property( self, label: str, property: str ) -> Iterator[Tuple[str, object]]:
        raise NotImplementedError( "Not implemented yet, sorry." )
    
    
    # endregion
    
    # region AbstractDestination
    
    
    @override
    def on_endpoint_create_folder( self, name: str ) -> AbstractDestination:
        """
        OVERRIDE AbstractDestination
        Does nothing
        """
        return self
    
    
    @override
    def on_endpoint_add_data( self, data: object ):
        warnings.warn( "This endpoint «{}» does not support the adding of arbitrary (non-node/edge) data «{}». This action has been ignored.".format( self, data ) )
    
    
    @override
    def on_endpoint_add_edge( self, edge: Edge ):
        """
        Adds an edge-csv
        """
        self.__writer.write_edge( edge )
    
    
    @override
    def on_endpoint_add_node( self, node: Node ):
        """
        OVERRIDE
        Write a node
        """
        assert all( node.properties.keys() )
        
        try:
            self.__writer.write_node( node )
        except Exception as ex:
            ss = ["Failed to write node. See causing error for details. Node details follow:",
                  "-- label = {}".format( node.label ),
                  "-- uid = {}".format( node.uid ),
                  "\n--",
                  "\n-- ".join( "{} = {}".format( k, v ) for k, v in node.properties.items() )]
            
            raise ValueError( "\n".join( ss ) ) from ex
    
    
    @override
    def on_endpoint_flush( self ) -> None:
        """
        OVERRIDE
        Flush 
        """
        self.__writer.close_all()
        
        
        # endregion AbstractDestination


class GexfEndpoint( AbstractFileEndpoint ):
    def _FILEENDPOINT_get_file_type( self ):
        return "GEXF"
    
    
    def _FILEENDPOINT_create_content( self, data: EdgeNodeDict ) -> None:
        TEMPLATE = \
            """
            <gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
                <meta lastmodifieddate="2017-04-20">
                    <creator>$(APP_DISPLAY_NAME)</creator>
                    <description>This file was exported by $(APP_DISPLAY_NAME)'s GephiExport plugin</description>
                </meta>
                <graph mode="static" defaultedgetype="directed">
                    <attributes class="node">
        {0}
                    </attributes>
                    <attributes class="edge">
        {1}
                    </attributes>
                    <nodes>
        {2}
                    </nodes>
                    <edges>
        {3}
                    </edges>
                </graph>
            </gexf>
            """
        
        TEMPLATE = MENV.host.substitute_text( TEMPLATE )
        
        node_xml = []
        edge_xml = []
        node_attrs = { }
        node_attr_xml = []
        edge_attrs = { }
        edge_attr_xml = []
        
        for node, node_id in data.nodes_and_ids:
            node_xml.append( '                <node id="{0}" label="{1}">'.format( node_id, node.label ) )
            self.__write_attributes( node, node_attr_xml, node_attrs, node_xml )
            node_xml.append( '                </node>' )
        
        for edge, edge_id, start_id, end_id in data.edges_and_ids:
            edge_xml.append( '                <edge id="{0}" label="{1}" source="{2}" target="{3}">'.format( edge_id, edge.label, start_id, end_id ) )
            self.__write_attributes( edge, edge_attr_xml, edge_attrs, edge_xml )
            edge_xml.append( '                </edge>' )
        
        return TEMPLATE.format( "\n".join( node_attr_xml ), "\n".join( edge_attr_xml ), "\n".join( node_xml ), "\n".join( edge_xml ) )
    
    
    @staticmethod
    def __write_attributes( entity: Union[Edge, Node], attr_xml: List[str], attrs, xml: List[str] ):
        xml.append( '                    <attvalues>' )
        for k, v in entity.properties.items():
            if k not in attrs:
                aid = len( attrs )
                attrs[k] = aid
                attr_xml.append( '                <attribute id="{0}" title="{1}" type="string"/>'.format( aid, k ) )
            else:
                aid = attrs[k]
            
            xml.append( '                        <attvalue for="{0}" value="{1}"/>'.format( aid, str( v ) ) )
        xml.append( '                    </attvalues>' )


class EdgeCsvEndpoint( AbstractFileEndpoint ):
    def _FILEENDPOINT_get_file_type( self ) -> str:
        return "CSV"
    
    
    def _FILEENDPOINT_create_content( self, data: EdgeNodeDict ) -> str:
        r = []
        
        r.append( "source,target" )
        
        for edge in data.edges:
            r.append( "{},{}".format( edge.start.uid.replace( ",", "." ), edge.end.uid.replace( ",", "." ) ) )
        
        return "\n".join( r )


class VisJsEndpoint( AbstractFileEndpoint ):
    def _FILEENDPOINT_get_file_type( self ) -> str:
        return "VISJS"
    
    
    def _FILEENDPOINT_create_content( self, data: EdgeNodeDict ) -> str:
        HTML_T = file_helper.read_all_text( path.join( file_helper.get_directory( __file__, 2 ), "misc_resources", "vis_js_template.html" ) )
        
        HTML_T = HTML_T.replace( "$(TITLE)", MENV.name + " " + self._FILEENDPOINT_get_file_type() + " endpoint: '" + self.endpoint_name + "'" )
        HTML_T = HTML_T.replace( "$(COMMENT)", "File automatically generated by NeoCommand/BIO42. Please replace this line with your own description." )
        
        r = []
        
        for node, node_id in data.nodes_and_ids:
            # {id: 1, label: 'Node 1'},
            r.append( "{id: " + str( node_id ) + ", label: '" + node.uid + "'}," )
        
        HTML_T = HTML_T.replace( "$(NODES)", "\n".join( r ) )
        
        r = []
        
        for edge, edge_id, start_id, end_id in data.edges_and_ids:
            # "{from: 1, to: 3},"
            r.append( "{from: " + start_id + ", to: " + end_id + "}," )
        
        HTML_T = HTML_T.replace( "$(EDGES)", "\n".join( r ) )
        
        return HTML_T


class EchoingEndpoint( AbstractDestination, IVisualisable ):
    """
    An write-only endpoint that echos data to the terminal.
    """
    FIXED_NAME = "echo"
    
    
    def on_get_name( self ) -> str:
        return self.FIXED_NAME
    
    
    def on_endpoint_set_name( self, value: str ):
        raise ValueError( "Cannot set the name of a system endpoint «{}».".format( self.endpoint_name ) )
    
    
    def on_endpoint_flush( self ) -> None:
        MCMD.print( "---ENDPOINT-FLUSH---" )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = "echo",
                       doc = "Echos output to std. out.",
                       type_name = "ECHO_EP",
                       value = "Maps I/O to echo",
                       colour = self.ENDPOINT_COLOUR,
                       icon = "export" )
    
    
    def __str__( self ) -> str:
        return "ECHO_EP"
    
    
    def __init__( self, title = "echo" ) -> None:
        super().__init__()
        self.title = title
    
    
    def __print( self, message: str ):
        MCMD.print( "{}) {}".format( self.title, message ) )
    
    
    def __print_properties( self, properties: Dict[str, object] ):
        if not properties.items():
            return
        
        items = sorted( properties.items(), key = lambda x: str( x[0] ) )
        longest = max( len( str( item[0] ) ) for item in items )
        
        for k, v in items:
            MCMD.print( "{})            {} = {}".format( self.title, str( k ).ljust( longest ), v ) )
    
    
    def on_endpoint_create_folder( self, name: str ) -> "AbstractDestination":
        self.__print( name + "/" )
        return EchoingEndpoint( self.title + "/" + name )
    
    
    def on_endpoint_add_data( self, data: object ):
        self.__print( "DATA {}".format( data ) )
    
    
    def on_endpoint_add_edge( self, edge: Edge ):
        self.__print( "EDGE ( {} «{}» )----[ {} ]---->( {} «{}» )".format( edge.start.label, edge.start.uid, edge.label, edge.end.label, edge.end.uid ) )
        self.__print_properties( edge.properties )
    
    
    def on_endpoint_add_node( self, node: Node ):
        self.__print( "NODE ( {} «{}» )".format( node.label, node.uid ) )
        self.__print_properties( node.properties )


ECHOING_ENDPOINT = EchoingEndpoint()


class CountingEndpointWrapper( AbstractDestination ):
    """
    Wraps another endpoint and counts the operations thereupon.
    """
    
    
    def on_endpoint_set_name( self, value: str ):
        raise ValueError( "Cannot set the name of the endpoint through a `CountingEndpointWrapper`." )
    
    
    def on_get_name( self ) -> str:
        return self.__endpoint.endpoint_name
    
    
    def __init__( self, endpoint: AbstractDestination ):
        super().__init__()
        self.__endpoint = endpoint
        self.num_nodes = 0
        self.num_edges = 0
    
    
    @override
    def on_endpoint_add_data( self, data: object ):
        return self.__endpoint.endpoint_add_data( data )
    
    
    def on_endpoint_add_node( self, node: Node ):
        self.num_nodes += 1
        return self.__endpoint.endpoint_add_node( node )
    
    
    def on_endpoint_add_edge( self, edge: Edge ):
        self.num_edges += 1
        return self.__endpoint.endpoint_add_edge( edge )
    
    
    def on_endpoint_create_folder( self, name: str ) -> "AbstractDestination":
        return self.__endpoint.endpoint_create_folder( name = name )
    
    
    def on_endpoint_flush( self ) -> None:
        return self.__endpoint.endpoint_flush()
    
    
    def __str__( self ) -> str:
        return "{} nodes and {} edges to {}".format( self.num_nodes, self.num_edges, self.__endpoint )
    
    
    def visualisable_info( self ) -> UiInfo:
        return self.__endpoint.visualisable_info()
