"""
Creates and registers additional string coercers.
"""
from typing import List

import stringcoercion

# Register coercers
from neocommand.core.core import CORE
from neocommand.core.annotations import TEdgeLabel, TEntityProperty, TNodeLabel
from stringcoercion import CoercionInfo


class __EndpointCoercer( stringcoercion.AbstractEnumCoercer ):
    
    
    def can_handle( self, info: CoercionInfo ):
        from neocommand.endpoints import AbstractEndpoint
        return info.annotation.is_directly_below( AbstractEndpoint )
    
    
    def get_options( self, args: CoercionInfo ) -> List[object]:
        return CORE.endpoint_manager
    
    
    def get_option_name( self, value ):
        return value.endpoint_name


class __B( stringcoercion.AbstractEnumCoercer ):
    
    def coerce( self, info: CoercionInfo ):
        try:
            super().coerce( info )
        except stringcoercion.CoercionError:
            return info.source
    
    
    def can_handle( self, info: CoercionInfo ):
        return info.annotation.type_or_optional_type in (TEdgeLabel, TNodeLabel, TEntityProperty)
    
    
    def get_options( self, info: CoercionInfo ) -> List[object]:
        r = []
        
        if info.annotation.is_optional:
            r.append( None )
        
        if info.annotation.type_or_optional_type is TEdgeLabel:
            r.extend( CORE.name_cache.edge_labels() )
        elif info.annotation.type_or_optional_type is TNodeLabel:
            r.extend( CORE.name_cache.node_labels() )
        elif info.annotation.type_or_optional_type is TEntityProperty:
            r.extend( CORE.name_cache.properties( info.annotation.type_label() ) )
        
        return r


def init():
    stringcoercion.register( __EndpointCoercer(), __B() )
