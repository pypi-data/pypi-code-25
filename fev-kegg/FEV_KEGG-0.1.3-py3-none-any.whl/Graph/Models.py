from math import ceil

import networkx.algorithms.components
import networkx.algorithms.operators.all
from typing import List, Set, Tuple, Generator, Iterable

from FEV_KEGG.Graph import Elements
from FEV_KEGG.Graph.Implementations.NetworkX import NetworkX, MultiDiGraph, MultiGraph


class _CommonGraphApi(object):
    """
    Represents any type of graph. The library to implement graphs is chosen here.
    """
    # choose a lib as implementation of graphs
    implementationLib = NetworkX
    
    def __init__(self, underlyingRawGraph = None):        
        if underlyingRawGraph != None:
            self.underlyingRawGraph = underlyingRawGraph.copy()
        
        self.nodeCounts = None
        self.edgeCounts = None
        self.edgeElementCounts = None
    
    @property
    def name(self):
        return self.underlyingRawGraph.name
    @name.setter
    def name(self, name: str):
        self.underlyingRawGraph.name = name
        
    @classmethod
    def composeAll(cls, graphs: List['_CommonGraphApi'], name: str, pathwaySet = None) -> '_CommonGraphApi':
        """
        Simple UNION of node and edge lists. Node is defined by hash(). Edge is defined by node1,node2,hash(key) plus direction, if the graph is directed.
        """
        # for all implementations
        allUnderlyingGraphs = []
        
        for abstractGraph in graphs:
            underlyingGraph = abstractGraph.underlyingRawGraph
            allUnderlyingGraphs.append(underlyingGraph)
            
        # NetworkX was chosen as graph implementation
        if cls.implementationLib == NetworkX:
            
            newUnderlyingGraph = networkx.algorithms.operators.all.compose_all(allUnderlyingGraphs)
            newGraph = cls()
            newGraph.underlyingRawGraph = newUnderlyingGraph
            newGraph.name = name
            
            if pathwaySet is not None: # some graph had a set of pathways it was derived from, apply it to the new graph
                newGraph.pathwaySet = pathwaySet
            
            return newGraph
        
        # unknown implementation
        else:
            raise NotImplementedError
        
    def getNodes(self) -> List[Elements.Element]:
        """
        Returns a list of all nodes. Even though the type list does not enforce it, this should never return duplicates.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            return self.underlyingRawGraph.nodes
            
        # unknown implementation
        else:
            raise NotImplementedError
        
    def getEdges(self) -> List[Tuple]:
        """
        Return the list of all edges, defined by tuples of (node1, node2, element).
        This is NOT a copy, but the original internal list. Do NOT change while iterating! Make a copy instead: copy = list(getEdges())
        Only returns outgoing edges, so that no edge is reported twice.
        Even though the type list does not enforce it, this should never return duplicates.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationGraph == MultiDiGraph:
            
            return self.underlyingRawGraph.edges(keys=True)
        
        # unknown implementation
        else:
            raise NotImplementedError
        
    def addNodes(self, nodes: List[Elements.Element]):
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            self.underlyingRawGraph.add_nodes_from(nodes)
            
        # unknown implementation
        else:
            raise NotImplementedError
        
    def addEdges(self, edges: List[Tuple[Elements.Element, Elements.Element, Elements.Element]]):
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            self.underlyingRawGraph.add_edges_from(edges)
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def removeEdges(self, edges: List[Tuple]):
        """
        Removes all edges in the specified list. Each list entry has to be of type Tuple(node1, node2, element).
        If an edge to be removed does not exist, the next edge will be tried, without any error message.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            self.underlyingRawGraph.remove_edges_from(edges)
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def removeEdgesByElement(self, elements: Iterable[Elements.Element]):
        """
        Removes all edges associated with each Element.
        """
        # NetworkX.MultiDiGraph was chosen as graph implementation
        if self.__class__.implementationGraph == MultiDiGraph:
            
            allEdges = self.getEdges()
            
            edgesToBeRemoved = []
            
            for edgeTuple in allEdges:
                _, _, element = edgeTuple
                
                if element in elements:
                    edgesToBeRemoved.append(edgeTuple)
            
            self.removeEdges(edgesToBeRemoved)
                
        # unknown implementation
        else:
            raise NotImplementedError
    
    def getIsolatedNodes(self) -> List[Elements.Element]:
        """
        Returns a list of nodes without any edge to another node. Even though the type list does not enforce it, this should never return duplicates.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            return list(networkx.algorithms.isolate.isolates(self.underlyingRawGraph))
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def removeNodes(self, nodes: List[Elements.Element]):
        """
        Removes all nodes in passed list.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            self.underlyingRawGraph.remove_nodes_from(nodes)
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def removeIsolatedNodes(self):
        """
        Removes all nodes without any edge to another node.
        """
        self.removeNodes(self.getIsolatedNodes())
        
        return self
        
    def removeSmallComponents(self, upToNumberOfNodes: int):
        """
        Removes any isolated component of the graph with a total count of nodes <= upToNumberOfNodes.
        For a directed graph, this considers weakly connected components, too. This means that there do NOT have to be edges in both directions to be counted as a component.
        """
        components = self.getComponents()
        
        nodesToRemove = []
        
        for componentNodes in components:
            if len( componentNodes ) <= upToNumberOfNodes: # component too small
                nodesToRemove.extend(componentNodes)
        
        # remove this component completely
        self.removeNodes(nodesToRemove)
        
        return self
    
    def getComponents(self) -> Generator[Set, None, None]:
        """
        Gets any isolated component of the graph. Each represented by a set of their nodes.
        For a directed graph, this considers weakly connected components, too. This means that there do NOT have to be edges in both directions to be counted as a component.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            if isinstance(self, UndirectedMultiGraph): # undirected graph
                return networkx.algorithms.components.connected_components(self.underlyingRawGraph)
            
            elif isinstance(self, DirectedMultiGraph): # directed graph
                return networkx.algorithms.components.weakly_connected_components(self.underlyingRawGraph)
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def getLargestComponent(self) -> Set[Elements.Element]:
        """
        Returns the set of nodes from the largest component.
        """
        return max(self.getComponents(), key=len)
    
    def getSubgraph(self, byNodes:Iterable = None, byEdges:Iterable = None) -> '_CommonGraphApi':
        """
        Returns a copy of the subgraph specified by either the nodes or the edges passed to this function.
        If both are passed, only nodes are used.
        If nothing is passed, None is returned.
        """
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            if byNodes is not None:
                return self.copy(self.underlyingRawGraph.subgraph(byNodes))
                
            elif byEdges is not None:
                return self.copy(self.underlyingRawGraph.edge_subgraph(byEdges))
                
            else:
                return None
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def getEdgesElements(self) -> Set[Elements.Element]:
        """
        Return a set of all edge's element, extracted from edge tuple of (node1, node2, element).
        Element objects contained in multiple edges are only contained once in the set.
        """
        edges = self.getEdges()
        elementSet = set()
        for edge in edges:
            _, _, element = edge
            elementSet.add(element)
        return elementSet
    
    def copy(self, underlyingRawGraph = None) -> '_CommonGraphApi':
        """
        Returns a shallow copy.
        However, some attributes are explicitly copied (although each attribute might itself be shallowly copied):
        .underlyingRawGraph
        .name
        """
        copy = self.__class__(underlyingRawGraph = underlyingRawGraph)
        if underlyingRawGraph is None:
            copy.underlyingRawGraph = self.underlyingRawGraph.copy()
        
        return copy

    def difference(self, subtrahend: 'Graph to be subtracted', subtractNodes = False, updateName = False) -> '_CommonGraphApi':
        """
        Returns a graph copy containing all nodes present in this object; and all edges present in this object, but not in subtrahend.
        You may want to removeIsolatedNodes() afterwards, to remove nodes that now have no edge.
        
        If subtractNodes == True, also remove all nodes present in subtrahend from this object. 
        WARNING: This may remove edges that only exist in this object, because they are removed with their associated node!
        """
        copy = self.copy()
        subtrahendEdges = subtrahend.getEdges()
        copy.removeEdges(subtrahendEdges)
        
        if (subtractNodes == True):
            subtrahendNodes = subtrahend.getNodes()
            copy.removeNodes(subtrahendNodes)
            
        # update name
        if updateName:
            copy.name = 'Difference ( [' + self.name + '], [' + subtrahend.name + '] )'
        
        return copy
    
    def intersection(self, withGraph: 'Graph to be intersected with, allows list of graphs', addCount = False, updateName = False) -> '_CommonGraphApi':
        """
        Returns a graph copy containing all nodes and edges present in both, this object and the other graph.
        You may want to removeIsolatedNodes() afterwards, to remove nodes that now have no edge.
        
        If 'addCount' == True, the returned graph contains extra dicts:
            graph.nodeCounts[node] = number of organisms which contained this node
            graph.edgeCounts[(node, node, element)] = number of organisms which contained this edge 
            graph.edgeElementCounts[element] = number of organisms which contained this element
        """
        
        # check if a list of graphs was passed
        if not isinstance(withGraph, Iterable):
            withGraph = [withGraph]
        
        nodesA = self.getNodes()
        edgesA = self.getEdges()
        if updateName:
            newGraphNameList = [self.name]
        
        if addCount is True:
            # count nodes and edges per graph
            nodesCount = dict.fromkeys(nodesA, 1)
            edgesCount = dict.fromkeys(edgesA, 1)
            elementSet = set()
            for edge in edgesA:
                _, _, element = edge
                elementSet.add(element)
            edgeElementsCount = dict.fromkeys(elementSet, 1)
        
        nodesIntersection = set(nodesA)
        edgesIntersection = set(edgesA)
        
        for graph in withGraph:
            # intersect set of nodes
            nodesB = graph.getNodes()
            
            if addCount is True:
                for node in nodesB:
                    nodesCount[node] = nodesCount.get(node, 0) + 1
            
            nodesIntersection = nodesIntersection.intersection(nodesB)
            
            # intersect set of edges
            edgesB = graph.getEdges()
            
            if addCount is True:
                
                elementSet = set()
                
                for edge in edgesB:
                    edgesCount[edge] = edgesCount.get(edge, 0) + 1
                    
                    _, _, element = edge
                    elementSet.add(element)
                
                for element in elementSet:
                    edgeElementsCount[element] = edgeElementsCount.get(element, 0) + 1
                
            edgesIntersection = edgesIntersection.intersection(edgesB)
            
            if updateName:
                newGraphNameList.append(graph.name)
        
        # add intersected nodes and edges to new graph
        newGraph = self.__class__()
        newGraph.addNodes(nodesIntersection)
        newGraph.addEdges(edgesIntersection)
        
        # update name
        if updateName:
            newGraph.name = 'Intersection ( [' + '], ['.join(newGraphNameList) + '] )'
        
        # if requested, add node counts
        if addCount is True:
            newGraph.nodeCounts = nodesCount
            newGraph.edgeCounts = edgesCount
            newGraph.edgeElementCounts = edgeElementsCount
        
        return newGraph
    
    def majorityIntersection(self, withGraph: 'Graph to be majority-intersected with, allows list of graphs', majorityPercentage = 51, addCount = False, updateName = False) -> '_CommonGraphApi':
        """
        Returns a graph copy containing all nodes and edges present in a majority of graphs.
        The majority percentage means 'at least x%' and is rounded up. For example 90% of 11 organisms (including the organism this method is called on) would be ceiling(9,9) = 10 organisms.
        If the rounded majority total effectively equated to 100% of all graphs, regular intersection() is called instead.
        If only one graph is passed in 'withGraph' AND the rounded majority total effectively equates 1, regular union() is called instead.
        You may want to removeIsolatedNodes() afterwards, to remove nodes that now have no edge.
        
        If 'addCount' == True, the returned graph contains extra dicts:
            graph.nodeCounts[node] = number of organisms which contained this node
            graph.edgeCounts[(node, node, element)] = number of organisms which contained this edge 
            graph.edgeElementCounts[element] = number of organisms which contained this element
        """
        
        # check if majorityPercentage is sane
        if majorityPercentage <= 0 or majorityPercentage > 100:
            raise ValueError('Majority percentage is not a sane value (0 < percentage <= 100): ' + str(majorityPercentage))
        
        # check if a list of graphs was passed
        # calculate total number of graphs needed for majority
        if isinstance(withGraph, Iterable):
            withGraphLength = len( withGraph )
            majorityTotal = ceil((majorityPercentage/100) * (withGraphLength + 1))
            
            if majorityTotal >= (withGraphLength + 1): # effectively 100% majority needed, >= because of float rounding error
                return self.intersection(withGraph)
        else:
            if majorityPercentage <= 50: # effectively 'or', thus union
                return self.union(withGraph, addCount)
            else: # effectively 100% majority needed, thus intersection
                return self.intersection(withGraph)
        
        # multiple graphs passed, single graphs are completely handled above
        if updateName:
            newGraphNameList = [self.name]
        
        nodesA = self.getNodes()
        edgesA = self.getEdges()
        
        # count nodes and edges per graph
        nodesCount = dict.fromkeys(nodesA, 1)
        edgesCount = dict.fromkeys(edgesA, 1)
        
        if addCount is True:
            elementSet = set()
            for edge in edgesA:
                _, _, element = edge
                elementSet.add(element)
            edgeElementsCount = dict.fromkeys(elementSet, 1)
        
        for graph in withGraph:
            
            nodesB = graph.getNodes()
            for node in nodesB:
                nodesCount[node] = nodesCount.get(node, 0) + 1
            
            edgesB = graph.getEdges()
            
            if addCount is True:
                elementSet = set()
            
            for edge in edgesB:
                edgesCount[edge] = edgesCount.get(edge, 0) + 1
                
                if addCount is True:
                    _, _, element = edge
                    elementSet.add(element)
            
            if addCount is True:
                for element in elementSet:
                    edgeElementsCount[element] = edgeElementsCount.get(element, 0) + 1
            
            if updateName:
                newGraphNameList.append(graph.name)
        
        # remove nodes and edges with count < majorityTotal
        for item in list( nodesCount.items() ):
            node, count = item
            if count < majorityTotal: # count not high enough
                del nodesCount[node]
        
        for item in list( edgesCount.items() ):
            edge, count = item
            if count < majorityTotal: # count not high enough
                del edgesCount[edge]
        
        # add majority-intersected nodes and edges to new graph
        newGraph = self.__class__()
        newGraph.addNodes(nodesCount.keys())
        newGraph.addEdges(edgesCount.keys())
        
        # update name
        if updateName:
            newGraph.name = 'Majority-Intersection ' + str(majorityPercentage) + '% ( [' + '], ['.join(newGraphNameList) + '] )'
        
        # if requested, add node counts
        if addCount is True:
            newGraph.nodeCounts = nodesCount
            newGraph.edgeCounts = edgesCount
            newGraph.edgeElementCounts = edgeElementsCount
        
        return newGraph
        
    def union(self, withGraph: 'Graph to be unified with, allows list of graphs', addCount = False, updateName = False) -> '_CommonGraphApi':
        """
        Returns a graph copy containing all nodes and edges present in either, this object or the other graph.
        
        If 'addCount' == True, the returned graph contains extra dicts:
            graph.nodeCounts[node] = number of organisms which contained this node
            graph.edgeCounts[(node, node, element)] = number of organisms which contained this edge 
            graph.edgeElementCounts[element] = number of organisms which contained this element
        """
        
        # check if a list of graphs was passed
        if not isinstance(withGraph, Iterable):
            withGraph = [withGraph]
        
        nodesA = self.getNodes()
        edgesA = self.getEdges()
        if updateName:
            newGraphNameList = [self.name]
        
        if addCount is True:
            # count nodes and edges per graph
            nodesCount = dict.fromkeys(nodesA, 1)
            edgesCount = dict.fromkeys(edgesA, 1)
            elementSet = set()
            for edge in edgesA:
                _, _, element = edge
                elementSet.add(element)
            edgeElementsCount = dict.fromkeys(elementSet, 1)
            
            for graph in withGraph:
                
                # unify set of nodes
                nodesB = graph.getNodes()
                for node in nodesB:
                    nodesCount[node] = nodesCount.get(node, 0) + 1
                
                # unify set of edges
                edgesB = graph.getEdges()
                
                elementSet = set()
                
                for edge in edgesB:
                    edgesCount[edge] = edgesCount.get(edge, 0) + 1
                    
                    _, _, element = edge
                    elementSet.add(element)
                
                for element in elementSet:
                    edgeElementsCount[element] = edgeElementsCount.get(element, 0) + 1
                
                if updateName:
                    newGraphNameList.append(graph.name)
            
            nodesUnion = nodesCount.keys()
            edgesUnion = edgesCount.keys()
            
        else:
            
            nodesUnion = set(nodesA)
            edgesUnion = set(edgesA)
            
            for graph in withGraph:
                
                # unify set of nodes
                nodesB = graph.getNodes()
                nodesUnion = nodesUnion.union(nodesB)
                
                # unify set of edges
                edgesB = graph.getEdges()
                edgesUnion = edgesUnion.union(edgesB)
                
                if updateName:
                    newGraphNameList.append(graph.name)
        
        # add unified nodes and edges to new graph
        newGraph = self.__class__()
        newGraph.addNodes(nodesUnion)
        newGraph.addEdges(edgesUnion)
        
        # update name
        if updateName:
            newGraph.name = 'Union ( [' + '], ['.join(newGraphNameList) + '] )'
        
        # if requested, add node counts
        if addCount is True:
            newGraph.nodeCounts = nodesCount
            newGraph.edgeCounts = edgesCount
            newGraph.edgeElementCounts = edgeElementsCount 
        
        return newGraph
        
    
    def __eq__(self, other):
        """
        Considered equal, if identical memory addresses OR (same class AND same number of nodes and edges AND ismorphic). Isomorphism check is NP-hard! 
        """
        if self is other: # identical object -> True
            return True
        
        if isinstance(self, other.__class__): # same class
            
            # NetworkX was chosen as graph implementation
            if self.__class__.implementationLib == NetworkX:
                
                if self.underlyingRawGraph.order() == other.underlyingRawGraph.order() and self.underlyingRawGraph.size() == other.underlyingRawGraph.size(): # same number of nodes and edges (weight 1)
                    
                    if len( set(self.underlyingRawGraph.nodes).symmetric_difference( other.underlyingRawGraph.nodes ) ) == 0: # same node set
                        
                        if len( set(self.underlyingRawGraph.edges).symmetric_difference( other.underlyingRawGraph.edges ) ) == 0: # same edge set
                            
                            return True # -> True
                
            # unknown implementation
            else:
                raise NotImplementedError
        
        return False # everything else -> False
        
    def __ne__(self, other):
        return not self == other
    
    def replaceNode(self, oldNode: Elements.Element, newNode: Elements.Element):
        """
        Replaces a certain node, if present, with another node. Silently ignores non-existing nodes.
        """
        
        if oldNode.__class__ is not newNode.__class__:
            raise TypeError('classes of nodes do not match')
        
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            networkx.relabel_nodes(self.underlyingRawGraph, {oldNode : newNode}, copy = False)
            
        # unknown implementation
        else:
            raise NotImplementedError
        
    def replaceEdgeElement(self, edge:Tuple['node_1', 'node_2', 'edge_element'], newElement:Elements.Element, bothDirections: bool = False):
        """
        Replaces a certain edge, if present, with another edge. Silently ignores non-existing edge, does not add the new edge then. Treats both directions independently.
        """
        
        node1, node2, oldElement = edge
        
        if oldElement.__class__ is not newElement.__class__:
            raise TypeError('classes of edge elements do not match')
        
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            if self.underlyingRawGraph.has_edge(node1, node2, oldElement):
                self.removeEdge(node1, node2, oldElement, bothDirections = False)
                self.addEdge(node1, node2, newElement, isReversible = False)
                
            if bothDirections == True:
                if self.underlyingRawGraph.has_edge(node2, node1, oldElement):
                    self.removeEdge(node2, node1, oldElement, bothDirections = False)
                    self.addEdge(node2, node1, newElement, isReversible = False)
            
        # unknown implementation
        else:
            raise NotImplementedError
        
        
        
        

class DirectedMultiGraph(_CommonGraphApi):
    """
    Represents a directed multigraph.
    """
    
    implementationGraph = MultiDiGraph
    
    def __init__(self, underlyingRawGraph: 'implementationGraph' = None):
        _CommonGraphApi.__init__(self, underlyingRawGraph)
        if underlyingRawGraph == None:
            self.underlyingRawGraph = self.__class__.implementationGraph()
    
    
    def addEdge(self, node1: Elements.Element, node2: Elements.Element, key: Elements.Element, isReversible: bool = False):
        
        # NetworkX.MultiDiGraph was chosen as graph implementation
        if self.__class__.implementationGraph == MultiDiGraph:

            self.underlyingRawGraph.add_edge(node1, node2, key) # automatically creates node, if not already present
            if isReversible == True:
                self.underlyingRawGraph.add_edge(node2, node1, key) # also add reverse direction
                
        # unknown implementation
        else:
            raise NotImplementedError
        
    def removeEdge(self, node1: Elements.Element, node2: Elements.Element, key:Elements.Element, bothDirections: bool = False):
        """
        Removes the edge uniquely specified by the above four parameters.
        You may want to removeIsolatedNodes() afterwards, to remove nodes that now have no edge.
        """
        # NetworkX.MultiDiGraph was chosen as graph implementation
        if self.__class__.implementationGraph == MultiDiGraph:
            
            self.underlyingRawGraph.remove_edge(node1, node2, key)
            if bothDirections == True:
                self.underlyingRawGraph.remove_edge(node2, node1, key) # also add reverse direction
                
        # unknown implementation
        else:
            raise NotImplementedError
    
    def getUnidirectionalEdges(self) -> Set[Tuple]:
        """
        Return a set of all edge tuples (node1, node2, element) that have only one direction.
        """
        undirectedGraphKeeping = self.toUndirectedGraph(True)
        undirectedGraph = self.toUndirectedGraph(False)
        
        # NetworkX was chosen as graph implementation
        if self.__class__.implementationLib == NetworkX:
            
            differenceGraph = networkx.algorithms.operators.difference(undirectedGraphKeeping.underlyingRawGraph, undirectedGraph.underlyingRawGraph)
            edgeList = differenceGraph.edges(keys=True)
            return edgeList
            
        # unknown implementation
        else:
            raise NotImplementedError
    
    def getUnidirectionalEdgesElements(self) -> Set[Elements.Element]:
        """
        Return a set of Elements.Element attached to each each having only one direction.
        """
        unidirectionalEdges = self.getUnidirectionalEdges()
        elementSet = set()
        for edge in unidirectionalEdges:
            _, _, element = edge
            elementSet.add(element)
        return elementSet
        
    def toUndirectedGraph(self, keepUnidirectionalEdges = False) -> 'UndirectedMultiGraph':
        """
        Returns an undirected multi graph. If keepUnidirectionalEdges == False, keep only edges that exist in both directions, as defined by node1, node2, hash(key) 
        """
        return UndirectedMultiGraph.fromDirectedMultiGraph(self, keepUnidirectionalEdges)
        
        
class UndirectedMultiGraph(_CommonGraphApi):
    """
    Represents an undirected multi graph.
    """
    implementationGraph = MultiGraph
    
    def __init__(self, underlyingRawGraph: 'implementationGraph' = None):
        _CommonGraphApi.__init__(self, underlyingRawGraph)
        if underlyingRawGraph == None:
            self.underlyingRawGraph = self.__class__.implementationGraph()
        
    @classmethod
    def fromDirectedMultiGraph(cls, directedMultiGraph: DirectedMultiGraph, keepUnidirectionalEdges = False):
        instance = cls()
        
        # if the graph has a pathway set it was derived from, copy it, too
        if hasattr(directedMultiGraph, 'pathwaySet'):
            instance.pathwaySet = directedMultiGraph.pathwaySet.copy()
        
        # NetworkX was chosen as graph implementation
        if directedMultiGraph.__class__.implementationGraph == MultiDiGraph:
            
            instance.underlyingRawGraph = directedMultiGraph.underlyingRawGraph.to_undirected(reciprocal = not keepUnidirectionalEdges)
        
        # unknown implementation
        else:
            raise NotImplementedError
        
        return instance
    