from FEV_KEGG.Graph import Models
import networkx.classes
import os

LABEL_NAME = 'label'

def _addLabelAttribute(nxGraph: networkx.classes.MultiGraph):
    
    # add label to edges
    edges = nxGraph.edges(keys = True)

    attributeDict = dict()
    for edge in edges:
        attributeDict[edge] = edge[2].__str__()
    
    networkx.set_edge_attributes(nxGraph, attributeDict, LABEL_NAME)
    
    # add label to nodes
    nodes = nxGraph.nodes
    
    attributeDict = dict()
    for node in nodes:
        attributeDict[node] = node.__str__()
    
    networkx.set_node_attributes(nxGraph, attributeDict, LABEL_NAME)
    

def toGraphML(graph: Models._CommonGraphApi, file, addLabel = False):
    """
    Export 'graph' to 'file' in GraphML format.
    
    If 'addLabel' == True, add an attribute to nodes and edges called "label" (see LABEL_NAME) containing the string of the node's id, or the edge's key, repectively.
    This is especially useful if the tool you import this file into does not regularly read the id parameter. For example, Cytoscape does not for edges. 
    """
    nxGraph = graph.underlyingRawGraph
    if isinstance(nxGraph, networkx.classes.graph.Graph):
        
        if addLabel:
            _addLabelAttribute(nxGraph)
        
        dirName = os.path.dirname(file)
        if not os.path.isdir(dirName) and dirName != '':
            os.makedirs(os.path.dirname(file))
        
        networkx.write_graphml_xml(nxGraph, file + '.graphml', prettyprint=False)
        
    else:
        raise NotImplementedError


def toGML(graph: Models._CommonGraphApi, file, addLabel = False):
    """
    Export 'graph' to 'file' in GML format.
    
    If 'addLabel' == True, add an attribute to nodes and edges called "label" (see LABEL_NAME) containing the string of the node's id, or the edge's key, repectively.
    This is especially useful if the tool you import this file into does not regularly read the id parameter. For example, Cytoscape does not for edges. 
    """
    nxGraph = graph.underlyingRawGraph
    if isinstance(nxGraph, networkx.classes.graph.Graph):
        
        if addLabel:
            _addLabelAttribute(nxGraph)
            
        dirName = os.path.dirname(file)
        if not os.path.isdir(dirName) and dirName != '':
            os.makedirs(os.path.dirname(file))
        
        networkx.write_gml(nxGraph, file + '.gml', lambda x: x.__str__())
        
    else:
        raise NotImplementedError
    
def forCytoscape(graph: Models._CommonGraphApi, file):
    """
    Export 'graph' to 'file' in GraphML format, including some tweaks for Cytoscape.
    """
    toGraphML(graph, file, addLabel = True)