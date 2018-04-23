import neo4j.v1
import py2neo
from mhelper import array_helper
from neocommand import AbstractDestination, Edge, Node
from neocommand.core import constants
from neocommand.core.database_manager import DbManager, DbStats, IDbDriverSession


class Py2neoSession( IDbDriverSession ):
    """
    PY2NEO DRIVER
    """
    
    
    def __init__( self, db: DbManager ):
        self.driver = py2neo.Graph( "http://" + db.remote_address + ":" + db.remote_port, user = db.user_name, password = db.password, bolt = False )
        
        if not self.driver:
            raise ConnectionError( "Failed to obtain connection to server (no error returned)." )
        
        py2neo.http.socket_timeout = 604800  # 1 week in seconds
    
    
    def run( self, cypher: str, parameters: dict, output: AbstractDestination ) -> DbStats:
        cursor = self.driver.run( cypher, parameters )
        
        try:
            self._convert_py2neo_entity( cursor, output )
            return DbStats( cypher, cursor.stats() )
        finally:
            cursor.close()
    
    
    def _convert_py2neo_entity( self, entity: object, output: AbstractDestination ) -> None:
        """
        Converts an arbitrary root_object to an `IEntity`.
        See the `docket_from_` methods to see what types are handled.
         
        :param entity:   Thing to convert 
        :return:         A `Docket` or `MemoryEndpoint` instance 
        """
        if isinstance( entity, py2neo.Cursor ):
            self._convert_py2neo_cursor( entity, output )
        elif isinstance( entity, py2neo.Node ):
            self._convert_py2neo_node( entity, output )
        elif isinstance( entity, py2neo.Relationship ):
            self._convert_py2neo_edge( entity, output )
        elif isinstance( entity, py2neo.Path ):
            self._convert_py2neo_path( entity, output )
        else:
            output.endpoint_add_data( entity )
    
    
    def _convert_py2neo_cursor( self, cursor: py2neo.Cursor, output: AbstractDestination ):
        for record in cursor:
            for entity in record:
                self._convert_py2neo_entity( entity, output )
    
    
    def _convert_py2neo_path( self, p: neo4j.v1.Path, output: AbstractDestination ) -> None:
        folder = output.endpoint_create_folder( "path" )
        
        for x in p:
            self._convert_py2neo_entity( x, folder )
    
    
    def _convert_py2neo_node( self, node: py2neo.Node, output: AbstractDestination ) -> None:
        output.endpoint_add_node( self._convert_py2neo_node_creator( node ) )
    
    
    def _convert_py2neo_edge( self, edge: py2neo.Relationship, output: AbstractDestination ) -> None:
        start = self._convert_py2neo_node_creator( edge.start_node() )
        end = self._convert_py2neo_node_creator( edge.end_node() )
        edge_ = Edge( label = array_helper.first_or_error( edge.types() ), start = start, end = end, properties = dict( edge ) )
        output.endpoint_add_edge( edge_ )
    
    
    @staticmethod
    def _convert_py2neo_node_creator( node: py2neo.Node ) -> py2neo.Node:
        """
        Converts a Node to a Docket.
        """
        if len( node.labels() ) != 1:
            raise ValueError( "Convert node to docket expected 1 label but {0} were received: {1}".format( len( node.labels() ), ", ".join( node.labels() ) ) )
        
        uid = node[constants.PROP_ALL_PRIMARY_KEY]
        
        if not uid:
            raise ValueError( "I can't read this node because it hasn't got a «{0}» property. Please make sure all your database nodes have a unique key named «{0}».".format( constants.PROP_ALL_PRIMARY_KEY ) )
        
        label = "".join( str( x ) for x in node.labels() )
        
        return Node( label = label, uid = uid, iid = None, properties = dict( node ) )