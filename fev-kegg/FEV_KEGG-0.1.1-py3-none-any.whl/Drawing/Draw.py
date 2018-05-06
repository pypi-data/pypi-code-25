import networkx.classes
import networkx.drawing.layout
from FEV_KEGG.Graph import Models
from FEV_KEGG.KEGG import File
from enum import Enum

def toPNG(graph: Models._CommonGraphApi, fileName: 'path/file', layout = 'neato'):
    
    nxGraph = graph.underlyingRawGraph
    if isinstance(nxGraph, networkx.classes.graph.Graph):
        
        File.createPath(fileName)
        agraph = networkx.nx_agraph.to_agraph(graph.underlyingRawGraph)
        agraph.layout()
        agraph.draw(fileName + '.png', format = 'png', prog = layout, args = '-Tpng')
        
    else:
        raise NotImplementedError

class NetworkxLayout(Enum):
    kamada_kawai = networkx.drawing.layout.kamada_kawai_layout
    random = networkx.drawing.layout.random_layout
    shell = networkx.drawing.layout.shell_layout
    spring = networkx.drawing.layout.spring_layout
    spectral = networkx.drawing.layout.spectral_layout
    fruchterman_reingold = networkx.drawing.layout.fruchterman_reingold_layout

def toWindow(graph: Models._CommonGraphApi, layout = NetworkxLayout):
    import matplotlib  # @UnresolvedImport
    nxGraph = graph.underlyingRawGraph
    if isinstance(nxGraph, networkx.classes.graph.Graph):
        positions = layout(nxGraph)
        networkx.drawing.nx_pylab.draw(nxGraph, pos = positions)
        
        edges = nxGraph.edges(keys = True)

        labelDict = dict()
        for n1, n2, key in edges:
            labelDict[(n1, n2)] = key.__str__()
        
        networkx.drawing.nx_pylab.draw_networkx_edge_labels(nxGraph, pos = positions, edge_labels = labelDict)
        matplotlib.pyplot.show()
        
    else:
        raise NotImplementedError