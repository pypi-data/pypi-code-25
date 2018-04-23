from neocommand.core import DbManager

def init():
    def __driver_1( m ):
        from .neo4jv1 import Neo4jv1Session
        return Neo4jv1Session( m )
    
    
    def __driver_2( m ):
        from .py2neo import Py2neoSession
        return Py2neoSession( m )
    
    
    DbManager.DRIVER_CLASSES["neo4jv1"] = __driver_1
    DbManager.DRIVER_CLASSES["py2neo"] = __driver_2
