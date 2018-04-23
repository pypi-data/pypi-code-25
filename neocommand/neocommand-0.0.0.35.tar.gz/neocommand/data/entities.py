"""
The database entity definitions.
"""
import warnings
from typing import Callable, Dict, Optional, Union

from intermake import EColour, IVisualisable, UiInfo
from mhelper import abstract, override, virtual, ResourceIcon


__author__ = "Martin Rusilowicz"

EDGE_UID_DELIMITER = ":"


@abstract
class IEntity( IVisualisable ):
    """
    Base class for graph entities.
    
    The entities:
        * may have a database presence, or not
        * may be complete or partial
        * are internally serialisable
        * are abstracted from the endpoint
        * inherit IVisualisable
    """
    
    
    # region IEntity
    
    def __init__( self, name: Optional[str], comment: Optional[str] ):
        """
        CONSTRUCTOR
        :param name: User-provided name on the docket. Can be `None`, in which case something else like the node UID is usually displayed. 
        :param comment: User-comment on the docket. Can also be `None`. 
        """
        self.name = name
        self.comment = comment
    
    
    # endregion
    
    
    # region IVisualisable
    
    @override
    @abstract
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE 
        """
        raise NotImplementedError( "abstract" )
    
    
    @override
    @virtual
    def __str__( self ):
        """
        OVERRIDE 
        """
        return self.name or "(untitled)"
    
    
    @override
    def __repr__( self ):
        """
        OVERRIDE 
        """
        return "{0}(name = «{1}»)".format( type( self ).__name__, self.name )
    
    # endregion


class Node( IEntity ):
    """
    Represents a graph edge, or a portion thereof.
    See the constructor for the fields.
    """
    
    
    def __init__( self,
                  *,
                  label: Optional[str] = None,
                  uid: Optional[str] = None,
                  iid: Optional[int] = None,
                  name: Optional[str] = None,
                  comment: Optional[str] = None,
                  properties: Dict[object, object] = None ):
        """
        :param *: 
        :param label: Label of the node, if known. Can be `None`. 
        :param uid: UID of the node, if known. Can be `None`.
        :param iid: IID of the node, if known. Can be `None`. 
        :param name: Inherited. Arbitrary comment on the name (not stored in the database). 
        :param comment: Inherited. Arbitrary comment on the edge (not stored in the database). 
        :param properties: Data on the node, if known. Use `None` if not known, or `{}` if it is known to be empty.
        """
        super().__init__( name, comment )
        
        self.label = label
        self.uid = uid
        self.iid = iid
        
        if properties is not None:
            self.properties = properties
        else:
            self.properties = { }
    
    
    def __str__( self ):
        if self.name:
            return self.name
        elif self.label and self.uid:
            return "{}::{}".format( self.label, self.uid )
        elif self.iid:
            return "{}".format( self.iid )
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       doc = self.comment,
                       type_name = "Node" if self.visualisable_is_loaded() else "Node*",
                       value = self.description(),
                       colour = EColour.BLUE,
                       icon = ResourceIcon( "node" ),
                       extra = { "label"     : self.label,
                                 "uid"       : self.uid,
                                 "properties": self.properties } )
    
    
    def description( self ):
        if self.label and self.uid:
            return self.label + " " + self.uid
        elif self.iid:
            return "#{0}".format( self.iid )
        else:
            return "?"


class Edge( IEntity ):
    """
    Represents a graph node, or a portion thereof.
    See the constructor for the fields.
    """
    
    
    def __init__( self,
                  *,
                  label: str,
                  start: Node,
                  end: Node,
                  name: Optional[str] = None,
                  comment: Optional[str] = None,
                  iid: Optional[int] = None,
                  properties: Optional[Dict[object, object]] ):
        """
        :param *: 
        :param name:        Inherited. Arbitrary comment on the name (not stored in the database). 
        :param comment:     Inherited. Arbitrary comment on the edge (not stored in the database).  
        :param iid:         Same as for `Node` 
        :param label:       Same as for `Node`  
        :param start:       Start node. 
        :param end:         End node. 
        :param properties:  Same as for `Node` 
        """
        super().__init__( name, comment )
        self.label = label
        self.start = start
        self.iid = iid
        self.end = end
        self.properties = properties
    
    
    def __str__( self ):
        return "{}-[{}:{}]->{}".format( self.start, self.iid if self.iid is not None else "", self.label, self.end )
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       doc = self.comment,
                       type_name = "Edge" if self.visualisable_is_loaded() else "Edge*",
                       value = self.value_description(),
                       colour = EColour.GREEN,
                       icon = ResourceIcon( "edge" ),
                       extra = { "label"     : self.label,
                                 "start"     : self.start,
                                 "end"       : self.end,
                                 "properties": self.properties } )
    
    
    def value_description( self ):
        if self.label is not None:
            return "{0} ➙{1}➙ {2}".format( self.start, self.label, self.end )
        elif self.iid is not None:
            return "{0} ➙#{1}➙ {2}".format( self.start, self.iid, self.end )
        else:
            return "{0} ➙?➙ {2}".format( self.start, self.iid, self.end )


# noinspection PyDeprecation
def iterate_all( root: object,
                 filter: Union[None, type, Callable[[object], bool]] = None ):
    """
    Give a starting docket, iterates that docket and all its children (if it is a folder)
    
    :param filter: Filter on type 
    :param root: Where to start 
    :return: Iterator over all contents 
    """
    warnings.warn( "This function is deprecated, please use the corresponding function on the endpoint itself.", DeprecationWarning )
    from neocommand import MemoryEndpoint

    if isinstance( filter, type ):
        the_type = filter
        filter = lambda x: isinstance( x, the_type )
    
    if filter is None or filter( root ):
        yield root
    
    if isinstance( root, MemoryEndpoint ):
        for a in root.contents:
            yield from iterate_all( a, filter )
    elif isinstance( root, Edge ):
        yield from iterate_all( root.start, filter )
        yield from iterate_all( root.end, filter )
