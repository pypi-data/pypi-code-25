from typing import List, Optional, Dict, cast

from intermake.engine.environment import MENV
from mhelper import exception_helper as ExceptionHelper

from neocommand.data.entities import Node


_AMO_ = "neocommand.endpoints.bases.AbstractMasterOrigin"
_QUICK_NAME_TABLE_KEY = "quick_name_table"


class _NameLookupSettings:
    def __init__( self ):
        self.quick_name_table = { }


class __NameLookup:
    def __init__( self ):
        self.__data: _NameLookupSettings = None
    
    
    def __ensure_loaded( self ) -> Dict[str, str]:
        if self.__data is None:
            self.__data = MENV.local_data.store.bind( _QUICK_NAME_TABLE_KEY, _NameLookupSettings() )
        
        return cast( Dict[str, str], self.__data.quick_name_table )
    
    
    def __getitem__( self, label ):
        result = self.__ensure_loaded().get( label )
        
        if not result:
            raise NotImplementedError( "Cannot get a quick name for nodes with the label «{0}» because obtaining quick names for nodes with this label isn't supported. Please specify a supported label instead or use the `set_quick_name` command to add support for nodes with this label.".format( label ) )
        
        return result
    
    
    def update( self, values: Dict[str, str] ):
        data = self.__ensure_loaded()
        needs_save = False
        
        for label, property in values.items():
            if label not in data:
                data[label] = property
                needs_save = True
        
        if needs_save:
            self.__save()
    
    
    def __setitem__( self, label, property ):
        self.__ensure_loaded()[label] = property
        self.__save()
    
    
    def __save( self ):
        MENV.local_data.store.commit( _QUICK_NAME_TABLE_KEY )
    
    
    def read_name( self, node: Node, lookup: _AMO_ ) -> str:
        property = self[node.label]
        
        result = node.properties.get( property )
        
        if result is None:
            if node.uid is not None:
                result = lookup.origin_get_node_property_by_uid( node.label, node.uid, node.property )
            elif node.iid is not None:
                result = lookup.origin_get_node_property_by_iid( node.iid, node.property )
            else:
                raise ValueError( "Cannot obtain a property for this node because it has neither a UID nor an IID." )
            
            if result is None:
                raise ValueError( "Cannot get the quick_node_name of the node «{0}». The quick_node_name property is «{1}». Check that the node exists and that this property is present. If the property is missing you may wish to change the quick_node_name property via the `set_quick_name` command.".format( node, property ) )
        
        ExceptionHelper.assert_type( "quick_node_name result", result, str )
        
        return result
    
    
    def find_name( self, label: str, uid: str, lookup: _AMO_ ) -> Optional[str]:
        """
        Given a `label` and a `uid`, returns the string that best describes this (e.g. `description` for a `Sequence`, or `scientific_name` for a `Taxon`)
        """
        return self.read_name( Node( label = label, uid = uid, iid = None, name = None, comment = None, properties = { } ), lookup )


name_lookup = __NameLookup()

__GET_NODE_LABELS = None


def node_labels( database: object ) -> List[str]:
    """
    All node labels
    """
    global __GET_NODE_LABELS
    
    if __GET_NODE_LABELS is None:
        from neocommand.api.plugin_classes.script import Script
        __GET_NODE_LABELS = Script( description = "Gets the distinct labels in the database",
                                    cypher = "MATCH (n) RETURN DISTINCT LABELS(n)" )
    
    from neocommand.endpoints.standard import DbEndpoint, MemoryEndpoint
    assert isinstance( database, DbEndpoint )
    ep = MemoryEndpoint()
    __GET_NODE_LABELS( database = database,
                       output = ep,
                       quiet = True )
    return ep.as_text()
