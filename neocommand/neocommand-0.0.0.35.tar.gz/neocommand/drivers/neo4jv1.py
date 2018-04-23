import neo4j.v1
import py2neo
from neocommand import AbstractDestination, Node, Edge
from neocommand.core import constants
from neocommand.core.database_manager import DbManager, DbStats, IDbDriverSession


class Neo4jv1Session( IDbDriverSession ):
    """
    NEO4J DRIVER
    """
    __neo4j_v1_driver_object = None
    
    
    def __init__( self, db: DbManager ):
        cls = type( self )
        
        if cls.__neo4j_v1_driver_object is None:
            url = "bolt://" + db.remote_address + ":7687"
            auth = neo4j.v1.basic_auth( db.user_name, db.password )
            cls.__neo4j_v1_driver_object = neo4j.v1.GraphDatabase.driver( url, auth = auth )
        else:
            url = None
        
        try:
            self.driver = cls.__neo4j_v1_driver_object.session()
        except Exception as ex:
            raise ConnectionError( "Failed to connect to the database using the following connection: URL = «{0}», auth = «{1}», password = «{2}». The error returned is «{3}: {4}»".format( url, db.user_name, "*****" if db.password else "[MISSING]", type( ex ).__name__, ex ) )
    
    
    def run( self, cypher: str, parameters: dict, output: AbstractDestination ) -> DbStats:
        cursor = self.driver.run( cypher, parameters )
        self._convert_neo4j_entity( cursor, output )
        return DbStats( cypher, cursor.consume().counters.__dict__ )
    
    
    def _convert_neo4j_entity( self, entity: object, output: AbstractDestination ) -> None:
        if isinstance( entity, neo4j.v1.StatementResult ):
            self._convert_neo4j_cursor( entity, output )
        elif isinstance( entity, neo4j.v1.Node ):
            self._convert_neo4j_node( entity, output )
        elif isinstance( entity, neo4j.v1.Relationship ):
            self.convert_neo4j_edge( entity, output )
        elif isinstance( entity, neo4j.v1.Path ):
            self._convert_neo4j_path( entity, output )
        else:
            output.endpoint_add_data( entity )
    
    
    def _convert_neo4j_cursor( self, cursor: neo4j.v1.StatementResult, output: AbstractDestination ):
        for record in cursor:
            for name, entity in record.items():
                self._convert_neo4j_entity( entity, output )
    
    
    def _convert_neo4j_path( self, p: py2neo.Path, output: AbstractDestination ) -> None:
        folder = output.endpoint_create_folder( "path" )
        
        for x in p:
            self._convert_neo4j_entity( x, folder )
    
    
    @staticmethod
    def _convert_neo4j_node( node: neo4j.v1.Node, output: AbstractDestination ) -> None:
        """
        Converts a Node to a Docket.
        """
        if len( node.labels ) != 1:
            raise ValueError( "Convert node to docket expected 1 label but {0} were received: {1}".format( len( node.labels() ), ", ".join( node.labels() ) ) )
        
        uid = node[constants.PROP_ALL_PRIMARY_KEY]
        
        if not uid:
            raise ValueError( "I can't read this node because it hasn't got a «{0}» property. Please make sure all your database nodes have a unique key named «{0}».".format( constants.PROP_ALL_PRIMARY_KEY ) )
        
        label = "".join( str( x ) for x in node.labels )
        
        output.endpoint_create_node( label = label, uid = uid, properties = dict( node ) )
    
    
    @staticmethod
    def convert_neo4j_edge( edge: neo4j.v1.Relationship, output: AbstractDestination ) -> None:
        start = Node( iid = edge.start )
        end = Node( iid = edge.end )
        edge_ = Edge( label = edge.type, iid = edge.id, start = start, end = end, properties = dict( edge ) )
        output.endpoint_add_edge( edge_ )