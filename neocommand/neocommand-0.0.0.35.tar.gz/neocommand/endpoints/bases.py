import warnings
from typing import Iterator, Tuple, Optional, Dict, List, Union, Type, TypeVar
from intermake import MENV, MCMD, IVisualisable, UiInfo, EColour 
from mhelper import NotSupportedError, virtual, abstract, sealed, SwitchError, array_helper, Filename, EFileMode, override, file_helper, ResourceIcon

from neocommand.data.entities import IEntity, Edge, Node, iterate_all
from neocommand.helpers.resolver import EntityResolver, EntityResolverUsage, EdgeNodeDict


T = TypeVar( "T" )

class AddFailedError( Exception ):
    """
    Endpoints raise this if an add fails for any reason.
    """
    pass


class InvalidEntityError( Exception ):
    """
    An error used when trying to retrieve an entity from the database when that entity does not exist in the database.
    """
    pass


class EndpointSupportError( NotSupportedError ):
    def __init__( self, endpoint ):
        super().__init__( "Sorry, but this «{}» endpoint does not support the requested feature. Please use a different endpoint for this purpose.".format( endpoint ) )


# noinspection PyAbstractClass
class AbstractEndpoint( IVisualisable ):
    """
    Base class for all `AbstractOrigin` and `AbstractDestination`
    """
    ENDPOINT_COLOUR = EColour.RED
    FILE_ENDPOINT_COLOUR = EColour.GREEN
    ENDPOINT_ICON = ResourceIcon( "parcel" )
    FILE_ENDPOINT_ICON = ResourceIcon( "parcel" )
    
    @property
    def endpoint_name( self ) -> str:
        """
        Obtains the user-provided name for the endpoint.
        """
        return self.on_get_name()
    
    
    @endpoint_name.setter
    def endpoint_name( self, value: str ):
        """
        SETTER 
        """
        self.on_endpoint_set_name( value )
    
    
    @virtual
    def on_endpoint_deleted( self ) -> None:
        """
        Allows handling if the endpoint is deleted by the user.
        
        :except Exception: The endpoint may raise any exception, this prevents deletion.
        """
        pass
    
    
    @abstract
    def on_get_name( self ) -> str:
        """
        The derived class should obtain the user-provided name for the endpoint.
        """
        raise NotImplementedError( "abstract" )
    
    
    @abstract
    def on_endpoint_set_name( self, value: str ):
        """
        The derived class should set the user-provided name for the endpoint to `value`.
        """
        raise NotImplementedError( "abstract" )


# noinspection PyAbstractClass
class AbstractOrigin( AbstractEndpoint ):
    """
    Endpoints that can read data. 
    """
    
    
    def origin_get_all( self ) -> Iterator[IEntity]:
        """
        Iterates over all nodes and edges.
        
        :except InvalidEntityError: Failed to locate entity
        :except NotSupportedError:  The endpoint does not support this feature
        """
        raise EndpointSupportError( self )
    
    
    def origin_get_all_nodes_property( self, label: str, property: str ) -> Iterator[Tuple[str, object]]:
        """
        Gets a UID-to-property dictionary for the specified node label.
         
        :param label:      Label of node 
        :param property:   Property to get 
        :return:           Iterator over UIDs and properties: Tuple[UID, property-value]
        :except NotSupportedError:  The endpoint does not support this feature
        """
        raise EndpointSupportError( self )


# noinspection PyAbstractClass
class AbstractMasterOrigin( AbstractOrigin ):
    """
    Special case of `AbstractOrigin` that allows individual lookups.
    """
    
    
    def origin_get_edge_by_iid( self, iid: int ) -> Edge:
        """
        Finds an edge by its internal identifier.
        
        :param iid:     IID 
        :return: The edge
        :except InvalidEntityError: Failed to locate entity
        :except NotSupportedError:  The endpoint does not support this feature
        """
        raise EndpointSupportError( self )
    
    
    def origin_get_edge_by_node_uids( self, label: str, start_label: str, end_label: str, start_uid: str, end_uid: str ) -> Edge:
        """
        Finds an edge by the UIDs of its nodes.
        :param label:           Label, of edge 
        :param start_label:     Label, of start node 
        :param end_label:       Label, of end node
        :param start_uid:       Uid, of start node 
        :param end_uid:         Uid, of end node
        :return: The edge 
        :except InvalidEntityError: Failed to locate entity 
        :except NotSupportedError:  The endpoint does not support this feature
        """
        raise EndpointSupportError( self )
    
    
    def origin_get_edge_by_node_iids( self, start_iid: int, end_iid: int ) -> Edge:
        """
        Finds an edge by the IIDs of its nodes.
        :param start_iid:   IID, of start node 
        :param end_iid:     IID, of end node 
        :return: The edge
        :except InvalidEntityError: Failed to locate entity 
        :except NotSupportedError:  The endpoint does not support this feature
        """
        raise EndpointSupportError( self )
    
    
    def origin_get_node_property_by_uid( self, label: str, uid: str, property: str ) -> Optional[object]:
        """
        Finds a single property of a node.
        :param label:       Label of node 
        :param uid:         UID of node 
        :param property:    Property to retrieve 
        :return:            The property, or `None` if the node was found but it doesn't have that property. 
        :except InvalidEntityError: Failed to locate entity
        :except NotSupportedError:  The endpoint does not support this feature
        """
        raise EndpointSupportError( self )
    
    
    def origin_get_node_property_by_iid( self, iid: int, property: str ) -> Optional[object]:
        """
        Finds a single property of a node.
        :param iid:         IID of node
        :param property:    Property to retrieve 
        :return:            The property, or `None` if the node was found but it doesn't have that property. 
        :except InvalidEntityError: Failed to locate entity
        :except NotSupportedError:  The endpoint does not support this feature 
        """
        raise EndpointSupportError( self )
    
    
    def origin_get_node_by_uid( self, label: str, uid: str ) -> Node:
        """
        Gets a specific node
        :param label:      Label of node
        :param uid:        UID of node
        :return:            The node
        :except InvalidEntityError: Failed to locate entity
        :except NotSupportedError:  The endpoint does not support this feature 
        """
        raise EndpointSupportError( self )
    
    
    def origin_get_node_by_iid( self, iid: int ) -> Node:
        """
        Gets a specific node
        :param iid:        IID
        :return:            The node
        :except InvalidEntityError: Failed to locate entity
        :except NotSupportedError:  The endpoint does not support this feature 
        """
        raise EndpointSupportError( self )


# noinspection PyAbstractClass
class AbstractDestination( AbstractEndpoint ):
    """
    Endpoints that can write data. 
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.__dirty = False
    
    
    def __str__( self ) -> str:
        """
        Returns a name that is better than the Python default.
        This function does not preclude a more detailed result from a derived class.
        """
        return "{}::{}".format( type( self ).__name__, self.endpoint_name )
    
    
    @sealed
    def endpoint_create_node( self, *, label: str, uid: str, properties: Dict[str, object] ):
        """
        Adds a node to the endpoint.

        If a node with the same label and UID does not already exists it should be created.
        The endpoint should update the specified `properties` on the node. object other properties should remain intact.
        
        :param label:       Node label 
        :param uid:         Node UID 
        :param properties:  Node properties to be updated.
                                ¡WARNING!
                                The caller should NOT assume that `properties` is not modified.
                                The implementing class is free to modify this dictionary (thus avoiding copies where unnecessary).
        :return:            The created node
        :except AddFailedError:     The add failed.
        :except NotSupportedError:  The endpoint does not support this feature
        """
        node = Node( label = label, uid = uid, properties = properties )
        self.endpoint_add_node( node )
        return node
    
    
    @sealed
    def endpoint_create_edge( self, *, label: str, start_label: str, start_uid: str, end_label: str, end_uid: str, properties: Dict[str, object] ):
        """
        Adds an edge to the endpoint.
        
        If an edge with the same label does not exist between the specified nodes, the edge should be created.
        The endpoint should update the specified `properties` on the edge. object other properties should remain intact.
        
        If the specified nodes do not exist, the behaviour is undefined (preferably an exception, though this cannot be guaranteed).
         
        :param label:           Edge type 
        :param start_label:     Starting node label 
        :param start_uid:       Starting node UID 
        :param end_label:       Ending node label 
        :param end_uid:         Ending node UID 
        :param properties:      Edge properties to be updated.
                                    ¡WARNING!
                                    The caller should NOT assume that `properties` is not modified.
                                    The implementing class is free to modify this dictionary (thus avoiding copies where unnecessary).
        :return: The created edge
        :except AddFailedError:     The add failed.
        :except NotSupportedError:  The endpoint does not support this feature
        """
        start = Node( label = start_label, uid = start_uid, properties = { } )
        end = Node( label = end_label, uid = end_uid, properties = { } )
        edge = Edge( label = label, start = start, end = end, properties = properties )
        self.endpoint_add_edge( edge )
        return edge
    
    
    @sealed
    def endpoint_add_node( self, node: Node ):
        """
        See `endpoint_create_node`. 
        """
        self.__dirty = True
        self.on_endpoint_add_node( node )
    
    
    @sealed
    def endpoint_add_edge( self, edge: Edge ):
        """
        See `endpoint_create_edge`.
        """
        self.__dirty = True
        self.on_endpoint_add_edge( edge )
    
    
    @sealed
    def endpoint_create_folder( self, name: str ) -> "AbstractDestination":
        """
        Adds a folder to the endpoint.
        
        Folders logically sort the results for the GUI, they may not have any actual effect if writing
        to a file, in which case the endpoint may just return it`self`.
        
        The default implementation of this function returns `self`, hence this function should never raise a `NotSupportedError`.
        
        :param name:                Folder name 
        :return:                    The new endpoint for this folder
        :except AddFailedError:     The add failed.
        """
        self.__dirty = True
        return self.on_endpoint_create_folder( name )
    
    
    @sealed
    def endpoint_add_data( self, data: object ) -> None:
        """
        Adds arbitrary data to the endpoint.
        Note that not all endpoints support the addition of arbitrary data.
        
        If the endpoint does not support this operation it will ideally fail silently or issue a warning, allowing other operations to proceed,
        This does not mean that this function will not raise, cases such as malformed data may still raise the appropriate exception.
        
        :param data: Data to add.
        :return: 
        """
        self.on_endpoint_add_data( data )
    
    
    @sealed
    def endpoint_add_entity( self, entity: IEntity ):
        """
        Adds a node or an edge to the endpoint.
        May not be used for arbitrary data.
        
        :param entity:  Node or edge to add.
        """
        if isinstance( entity, Edge ):
            self.endpoint_add_edge( entity )
        elif isinstance( entity, Node ):
            self.endpoint_add_node( entity )
        else:
            raise SwitchError( "entity", entity, instance = True )
    
    
    @abstract
    def on_endpoint_add_data( self, data: object ):
        """
        Abstracted implementation of `endpoint_add_data`.
        """
        raise NotImplementedError( "abstract" )
    
    
    @abstract
    def on_endpoint_add_node( self, node: Node ):
        """
        Abstracted implementation of `endpoint_add_node`.
        """
        raise NotImplementedError( "abstract" )
    
    
    @abstract
    def on_endpoint_add_edge( self, edge: Edge ):
        """
        Abstracted implementation of `endpoint_add_edge`.
        """
        raise NotImplementedError( "abstract" )
    
    
    @virtual
    def on_endpoint_create_folder( self, name: str ) -> "AbstractDestination":
        """
        Abstracted implementation of `endpoint_create_folder`.
        """
        return self
    
    
    @sealed
    def endpoint_flush( self ) -> None:
        """
        Flushes the endpoint.
        
        The endpoint should be capable of handling excessive (redundant or unnecessary) flushes.
        This must be called if changes are made.
        If this is not called, any changes made may or may not be committed, or the output file may be incomplete, though the
        endpoint should ensure to preserve the integrity of primary data-sources (i.e. the database).
        
        Implementation notice:
        This function is required even if the endpoint does not perform any flushing action. The default implementation raises
        a `NotSupportedError`, since missing functionality would cause more problematic issues, such as sporadic output corruption.
        """
        if self.__dirty:
            self.__dirty = False
            self.on_endpoint_flush()
    
    
    @abstract
    def on_endpoint_flush( self ) -> None:
        """
        Abstracted implementation of `endpoint_flush`.
        """
        raise NotImplementedError( "abstract" )


# noinspection PyAbstractClass
class AbstractListBackedEndpoint( AbstractOrigin, AbstractDestination ):
    def on_get_name( self ) -> str:
        return self.__name
    
    
    # noinspection PyMethodOverriding
    def on_endpoint_set_name( self, value: str ) -> None:
        self.__name = value
    
    
    def __init__( self, name: str, comment: Optional[str] ):
        super().__init__()
        self.__name = name
        self.comment = comment or ""
    
    
    def __len__( self ) -> int:
        """
        Folders have a length that is the size of the contents
        """
        if self.contents is not None:
            return len( self.contents )
        else:
            return -1
    
    
    @property
    def contents( self ) -> List[Optional[object]]:
        raise NotImplementedError( "abstract" )
    
    
    def on_endpoint_create_folder( self, name: str ) -> AbstractDestination:
        from neocommand.endpoints.standard import MemoryEndpoint
        result = MemoryEndpoint( name = name )
        self.contents.append( result )
        return result
    
    
    def on_endpoint_add_data( self, data: object ):
        self.contents.append( data )
    
    
    def on_endpoint_add_edge( self, edge: Edge ):
        self.contents.append( edge )
    
    
    def on_endpoint_add_node( self, node: Node ):
        self.contents.append( node )
    
    
    def origin_get_all( self ) -> Iterator[Union[Node, Edge]]:
        result = list( iterate_all( self, lambda x: isinstance( x, Node ) or isinstance( x, Edge ) ) )
        
        return result
    
    
    def origin_get_all_nodes_property( self, label: str, property: str ) -> Iterator[Tuple[str, object]]:
        def __filter( x ) -> bool:
            return isinstance( x, Node ) and x.label == label
        
        
        for x in iterate_all( self, __filter ):
            if x.data is not None and property in x.data:
                yield x.uid, x.data[property]
    
    
    def visualisable_info( self ) -> UiInfo:
        return super().visualisable_info().supplement( count = len( self ),
                                                       contents = self.contents )
    
    
    def only_child( self, expected: Optional[Type[T]] = None ) -> T:
        """
        Returns the only child of this folder, or `None` if it is empty.
        Raises a `ValueError` if there is more than 1 item.
        """
        if len( self ) == 0:
            raise ValueError( "Cannot obtain the only child of a {} «{}» because the folder doesn't contain any elements.".format( type( self ), self ) )
        elif len( self ) == 1:
            result = self.contents[0]

            from neocommand.endpoints.standard import MemoryEndpoint
            if isinstance( result, MemoryEndpoint ):
                result = result.only_child( expected )
            
            if expected is not None:
                if not isinstance( result, expected ):
                    raise ValueError( "Cannot obtain the only child of a {} «{}» because the result is of type «{}», not the expected type «{}».".format( type( self ), self, type( result ), expected ) )
            
            return result
        
        else:
            raise ValueError( "Cannot obtain the only child of a {} «{}» because the folder contains more than 1 child.".format( type( self ), self ) )
    
    
    def as_text( self ) -> List[str]:
        """
        Sometimes we want basic text from the database, such as UIDs or names.
        Our `DbManager` still gives back the results as `Docket`s, so we use this function to pull the text from the dockets into a simple list. 
        :return: 
        """
        result = [array_helper.decomplex( x ) for x in self.contents]  # due to mistakes in parsing, sometimes items are stored in the database as strings inside lists of length 1, this just pulls them out
        
        for x in result:
            if not isinstance( x, str ):
                raise ValueError( "At least one element is not `str` in `docket_to_text. The offending item is of type «{0}» and has a value of «{1}»".format( type( x ).__name__, repr( x ) ) )
        
        # noinspection PyTypeChecker
        return result
    
    
    def get_or_create_folder( self, path: str ) -> "List[AbstractListBackedEndpoint]":
        """
        Given a `/` separated path, locating or creating subfolders as necessary. Returns a list of the complete path.
        """
        if not path:
            return [self]
        
        path = path.replace( "\\", "/" )
        
        elements = path.split( "/" )
        results = []
        
        from neocommand.endpoints.standard import MemoryEndpoint
        current : MemoryEndpoint = self
        results.append( self )
        
        for element in elements:
            if element:
                element = MENV.host.translate_name( element )
                found = False
                
                for docket in current.contents:
                    if isinstance( docket, MemoryEndpoint ):
                        if MENV.host.translate_name( docket.endpoint_name ) == element:
                            current = docket  # type: MemoryEndpoint
                            found = True
                            break
                
                if not found:
                    new = MemoryEndpoint( name = element )
                    current.contents.append( new )
                    current = new
                
                results.append( current )
        
        return results


class AbstractFileEndpoint( AbstractDestination ):
    _EXT_GEXF = ".gexf"
    
    def __init__( self,
                  name: str,
                  file_name: Filename[EFileMode.WRITE, _EXT_GEXF],
                  resolver: Optional[AbstractMasterOrigin],
                  cache_enabled: bool,
                  enforce_enabled: bool ):
        super().__init__()
        self.__name = name
        self.__file_name = file_name
        self.__resolver = EntityResolver( resolver, cache_enabled, enforce_enabled )
        self.__edges: List[Edge] = []
        self.__nodes: List[Node] = []
    
    
    def __getstate__( self ) -> Dict[str, object]:
        return { "name"     : self.__name,
                 "file_name": self.__file_name,
                 "resolver" : self.__resolver }
    
    
    def __setstate__( self, state: Dict[str, object] ) -> None:
        self.__name = state["name"]
        self.__file_name = state["file_name"]
        self.__resolver = state["resolver"]
        self.__edges = []
        self.__nodes = []
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.__name,
                       doc = "{} endpoint to «{}»".format( self._FILEENDPOINT_get_file_type(), self.__file_name ),
                       type_name = "{}_EP".format( self._FILEENDPOINT_get_file_type() ),
                       value = self.__file_name,
                       colour = self.FILE_ENDPOINT_COLOUR,
                       icon = self.FILE_ENDPOINT_ICON,
                       extra = { "resolver"         : self.__resolver.name,
                                 "resolver_cached"  : self.__resolver.cache_enabled,
                                 "resolver_enforced": self.__resolver.enforce_enabled } )
    
    
    @property
    def file_name( self ) -> str:
        return self.__file_name
    
    
    def on_get_name( self ) -> str:
        return self.__name
    
    
    def on_endpoint_set_name( self, value: str ) -> None:
        self.__name = value
    
    
    @override
    def on_endpoint_add_data( self, data: object ):
        if data is None:
            return
        
        warnings.warn( "This {} endpoint «{}» does not support the adding of arbitrary (non-node/edge) data «{}». This action has been ignored.".format( self._FILEENDPOINT_get_file_type(), self, data ) )
    
    
    def on_endpoint_add_edge( self, edge: Edge ):
        self.__edges.append( edge )
    
    
    def on_endpoint_add_node( self, node: Node ):
        self.__nodes.append( node )
    
    
    def on_endpoint_flush( self ) -> None:
        resolver: EntityResolverUsage = self.__resolver.acquire()
        end = EdgeNodeDict( resolver, self.__nodes, self.__edges )
        text = self._FILEENDPOINT_create_content( end )
        
        if self.__file_name == "stdout":
            print( text )
        elif self.__file_name == "ui":
            MCMD.print( text )
        else:
            directory_name = file_helper.get_directory( self.__file_name )
            file_helper.create_directory( directory_name )
            file_helper.write_all_text( self.__file_name, text )
        
        MCMD.progress( "Flushed {} endpoint to disk: {}".format( self._FILEENDPOINT_get_file_type(), self.__file_name ) )
        MCMD.progress( "{} nodes and {} edges.".format( len( end.nodes_and_ids ), len( end.edges_and_ids ) ) )
        MCMD.progress( "{}".format( resolver.describe() ) )
        
        self.__edges.clear()
        self.__nodes.clear()
    
    
    def _FILEENDPOINT_get_file_type( self ) -> str:
        """
        The derived class should implement this method by returning a short string denoting the file type being written, e.g. "GEXF" or "XML".
        """
        raise NotImplementedError( "abstract" )
    
    
    def _FILEENDPOINT_create_content( self, data: "EdgeNodeDict" ) -> str:
        """
        The derived class should implement this method by converting the provided data to a string and returning it.
        """
        raise NotImplementedError( "abstract" )