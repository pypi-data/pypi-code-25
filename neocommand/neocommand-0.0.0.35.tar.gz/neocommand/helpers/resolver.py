from collections import OrderedDict
from typing import Optional, Dict, Sequence, List, Iterable, Tuple, ValuesView

from intermake.engine.environment import MCMD
from mhelper import NotSupportedError
from neocommand.data.entities import Edge, Node

_AMO_ = "neocommand.endpoints.bases.AbstractMasterOrigin"

class EntityResolver:
    """
    The `EntityResolver` manages an `AbstractMasterOrigin`, which is used to resolve incomplete database entities.
    """
    def __init__( self, endpoint: Optional[_AMO_] = None, cache_enabled: bool = True, enforce_enabled: bool = True ) -> None:
        self.name: str = endpoint.endpoint_name if endpoint is not None else None
        self.cache_enabled: bool = cache_enabled
        self.enforce_enabled: bool = enforce_enabled
    
    
    def acquire( self ):
        return EntityResolverUsage( self )
    
    
    def _get_origin( self ) -> Optional[_AMO_]:
        from neocommand.core.core import CORE
        
        if self.name is None:
            # None = default database
            result = CORE.endpoint_manager.get_database_endpoint( tolerant = True )
            
            if result is None:
                MCMD.warning( "There are empty nodes and due to a previous issue I cannot obtain their data. Some data may be missing from your output." )
        
        else:
            # Name = find named
            result = CORE.endpoint_manager.find_endpoint( self.name )
            
            if result is None:
                MCMD.warning( "There are empty nodes and due to a previous issue I cannot obtain their data. Some data may be missing from your output." )
        
        return result
    
    
    def __str__( self ) -> str:
        return self.name or "(default)"


class EntityResolverUsage:
    def __init__( self, resolver: EntityResolver ):
        self.__resolver: EntityResolver = resolver
        self.__origin: _AMO_ = resolver._get_origin()
        self.__used_missing_edge_warning: bool = False
        self.__used_missing_node_warning: bool = False
        self.__edge_cache: Dict[str, Edge] = { }
        self.__node_cache: Dict[str, Node] = { }
        self.__edge_count = 0
        self.__node_count = 0
    
    
    def __getstate__( self ) -> Dict[str, object]:
        raise NotSupportedError( "This class should not be serialised." )
    
    
    def describe( self ) -> str:
        return "{} nodes and {} edges resolved from {}.".format( self.__node_count, self.__edge_count, self.__origin )
    
    
    def is_node_valid( self, node: Node ) -> bool:
        assert node is not None
        
        return node.label and node.uid
    
    
    def is_edge_valid( self, edge: Edge ) -> bool:
        assert edge is not None
        
        return edge.label \
               and edge.start \
               and ((edge.start.label and edge.start.uid) or edge.start.iid) \
               and edge.end \
               and ((edge.end.label and edge.end.uid) or edge.end.iid)
    
    
    def get_node_cache_names( self, nodes: Sequence[Node] ) -> List[str]:
        results = []
        
        for node in nodes:
            if node.label is not None and node.uid is not None:
                results.append( "n" + node.label + "\t" + node.uid )
                break
        
        for node in nodes:
            if node.iid is not None:
                results.append( node.iid )
                break
        
        return results
    
    
    def get_edge_cache_names( self, edges: Sequence[Edge] ) -> List[str]:
        results = []
        
        for edge in edges:
            if edge.start is not None and edge.end is not None and edge.start.label is not None and edge.start.uid is not None and edge.end.label is not None and edge.end.uid is not None:
                results.append( "e" + edge.label + "\t" + edge.start.label + "\t" + edge.end.label + "\t" + edge.start.uid + "\t" + edge.end.uid )
                break
        
        for edge in edges:
            if edge.start is not None and edge.end is not None and edge.start.iid is not None and edge.end.iid is not None:
                results.append( "e" + str( edge.start.iid ) + "\t" + str( edge.end.iid ) )
                break
        
        for edge in edges:
            if edge.iid is not None:
                results.append( "e" + str( edge.start.iid ) + "\t" + str( edge.end.iid ) )
                break
        
        return results
    
    
    def prepare_node( self, node: Node ) -> None:
        if self.is_node_valid( node ):
            self.cache_node( (node,) )
    
    
    def prepare_edge( self, edge: Edge ) -> None:
        if self.is_edge_valid( edge ):
            self.cache_edge( (edge,) )
    
    
    def cache_node( self, nodes: Sequence[Node] ) -> None:
        first = nodes[0]
        
        if not self.is_node_valid( first ):
            raise ValueError( "Attempt to cache a node that itself is not complete is probably a mistake." )
        
        for name in self.get_node_cache_names( nodes ):
            self.__node_cache[name] = first
    
    
    def cache_edge( self, edges: Sequence[Edge], include_nodes: bool = True ) -> None:
        first = edges[0]
        
        assert self.is_edge_valid( first )
        
        if not self.__resolver.cache_enabled:
            return
        
        for name in self.get_edge_cache_names( edges ):
            self.__edge_cache[name] = first
        
        if include_nodes:
            if self.is_node_valid( first.start ):
                self.cache_node( [x.start for x in edges] )
            
            if self.is_node_valid( first.end ):
                self.cache_node( [x.end for x in edges] )
    
    
    def uncache_node( self, nodes: Sequence[Node] ) -> Optional[Node]:
        for name in self.get_node_cache_names( nodes ):
            result = self.__node_cache.get( name )
            
            if result is not None:
                return result
        
        return None
    
    
    def uncache_edge( self, edges: Sequence[Edge] ) -> Optional[Edge]:
        if not self.__resolver.cache_enabled:
            return None
        
        for name in self.get_edge_cache_names( edges ):
            result = self.__edge_cache.get( name )
            
            if result is not None:
                return result
        
        return None
    
    
    def resolve_node( self, node: Node ) -> Optional[Node]:
        if self.is_node_valid( node ):
            self.cache_node( (node,) )
            return node
        
        result = self.uncache_node( (node,) )
        
        if result is not None:
            return result
        
        if self.__origin is not None:
            if node.label is not None and node.uid is not None:
                result = self.__origin.origin_get_node_by_uid( node.label, node.uid )
            
            if result is None and node.iid is not None:
                result = self.__origin.origin_get_node_by_iid( node.iid )
        
        if result is not None:
            if not self.is_node_valid( result ):
                raise ValueError( "Attempt to resolve a node resulted in another node which also isn't resolved." )
            
            self.__node_count += 1
            self.cache_node( (result, node) )
            return result
        elif self.__resolver.enforce_enabled:
            raise ValueError( "Cannot make the node concrete because I can't find it or it doesn't exist in the database." )
        elif not self.__used_missing_node_warning:
            self.__used_missing_node_warning = True
            MCMD.warning( "Nodes without data have been detected. Some data may be missing from your output. See section `Needs resolve` in `neocommand/readme.md`." )
        
        return None
    
    
    def resolve_edge_nodes( self, include_nodes: bool, edge: Edge ) -> Edge:
        if not include_nodes:
            return edge
        
        assert self.is_edge_valid( edge )
        
        if not self.is_node_valid( edge.start ) or not self.is_node_valid( edge.end ):
            edge = Edge( label = edge.label,
                         start = self.resolve_node( edge.start ),
                         end = self.resolve_node( edge.end ),
                         name = edge.name,
                         comment = edge.comment,
                         iid = edge.iid,
                         properties = dict( edge.properties ) )
        
        return edge
    
    
    def resolve_entity( self, entity: object ) -> Optional[object]:
        if isinstance( entity, Edge ):
            return self.resolve_edge( entity )
        elif isinstance( entity, Node ):
            return self.resolve_node( entity )
        else:
            return entity
    
    
    def resolve_iter( self, iter: Iterable[object] ) -> Iterable[object]:
        for entity in iter:
            yield self.resolve_entity( entity )
    
    
    def resolve_edge( self, edge: Edge, include_nodes: bool = True ) -> Optional[Edge]:
        #
        # Already complete
        #
        if self.is_edge_valid( edge ):
            edge = self.resolve_edge_nodes( include_nodes, edge )
            self.cache_edge( (edge,) )
            return edge
        
        #
        # In cache
        #
        result = self.uncache_edge( (edge,) )
        
        if result is not None:
            return result
        
        #
        # From origin
        #
        if self.__origin is None:
            if edge.start is not None and edge.end is not None:
                if edge.start.label is not None and edge.start.uid is not None and edge.end.label is not None and edge.end.uid is not None:
                    result = self.__origin.origin_get_edge_by_node_uids( label = edge.label,
                                                                         start_label = edge.start.label,
                                                                         end_label = edge.end.label,
                                                                         start_uid = edge.start.uid,
                                                                         end_uid = edge.end.uid )
                elif edge.start.iid is not None and edge.end.iid is not None:
                    result = self.__origin.origin_get_edge_by_node_iids( start_iid = edge.start.iid, end_iid = edge.end.iid )
            
            if result is None and edge.iid is not None:
                result = self.__origin.origin_get_edge_by_iid( edge.iid )
        
        if result is not None:
            result = self.resolve_edge_nodes( include_nodes, result )
            self.__edge_count += 1
            self.cache_edge( (result, edge) )
            return result
        
        if self.__resolver.enforce_enabled:
            raise ValueError( "Cannot make the edge concrete because I can't find it or it doesn't exist in the database." )
        elif not self.__used_missing_edge_warning:
            self.__used_missing_edge_warning = True
            MCMD.warning( "Edges without nodes have been detected. Some data may be missing from your output. See section `needs-resolve` in `readme.md`." )
        
        return None


class EdgeNodeDict:
    """
    Holds, processes and manages the data passed to the `_FILEENDPOINT_create_content` function.
    """
    
    
    def __init__( self, resolver_: EntityResolverUsage, nodes_: List[Node], edges_: List[Edge] ):
        self.__resolver: EntityResolverUsage = resolver_
        self.__nodes: Dict[str, Tuple[Node, int]] = OrderedDict()
        self.__edges: Dict[str, Tuple[Edge, int]] = OrderedDict()
        
        for node in nodes_:
            resolver_.prepare_node( node )
        
        for edge in edges_:
            resolver_.prepare_edge( edge )
        
        for node in nodes_:
            self.__add_node_to_list( resolver_, node, self.__nodes )
        
        for edge in edges_:
            edge = resolver_.resolve_edge( edge )
            start, start_id = self.__add_node_to_list( resolver_, edge.start, self.__nodes )
            end, end_id = self.__add_node_to_list( resolver_, edge.end, self.__nodes )
            
            if edge is None:
                continue
            
            local_key = "\t".join( [edge.label, start.label, start.uid, end.label, end.uid] )
            
            if local_key in self.__edges:
                continue
            
            self.__edges[local_key] = edge, len( self.__edges ), start_id, end_id
    
    
    @property
    def nodes_and_ids( self ) -> ValuesView[Tuple[Node, int]]:
        """
        Obtains an iterator over tuples specifying
            * the nodes to write
            * their arbitrary IDs for this session.
        """
        return self.__nodes.values()
    
    
    @property
    def edges_and_ids( self ):
        """
        Obtains an iterator over tuples specifying
            * the edges to write
            * their arbitrary IDs for this session.
            * the id of the start node
            * the id of the end node
        """
        return self.__edges.values()
    
    
    @property
    def edges( self ):
        """
        Obtains an iterator the edges to write.
        """
        return (x[0] for x in self.__edges.values())
    
    
    @property
    def nodes( self ):
        """
        Obtains an iterator the nodes to write.
        """
        return (x[0] for x in self.__nodes.values())
    
    
    def __add_node_to_list( self, resolver: EntityResolverUsage, node: Node, nodes: Dict[str, Tuple[Node, int]] ) -> Tuple[Node, int]:
        node = resolver.resolve_node( node )
        
        local_key : str = self.__get_node_local_key( node )
        
        if local_key in nodes:
            return nodes[local_key]
        
        id_ = len( nodes )
        nodes[local_key] = node, id_
        
        return node, id_
    
    
    @staticmethod
    def __get_node_local_key( node: Node ) -> str:
        assert node.label
        assert node.uid
        
        luid = [str( node.label ), str( node.uid )]
        return "\t".join( luid )
    
    
    def get_node_id( self, node: Node ):
        """
        Gets the arbitrary id for this session of a particular node.
        
        :except KeyError: Node not present in this session
        """
        return self.__nodes[self.__get_node_local_key( node )][1]