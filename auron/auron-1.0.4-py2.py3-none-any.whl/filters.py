import networkx as nx
from auron import tools
from .tools import logging

from yuna import masternodes as mn
from auron import inductors as ix


def subgraphs(g):
    logger = logging.getLogger(__name__)
    logger.info('Merging subgraphs')

    graphs = list(nx.connected_component_subgraphs(g))

    gg = list()
    for graph in graphs:
        save = False
        for n in graph.nodes():
            if 'label' in graph.node[n]:
                label = graph.node[n]['label']
                if isinstance(label, mn.Terminal):
                    save = True

        if save is True:
            gg.append(graph)

    return nx.disjoint_union_all(gg)


def noise_nodes(g, gds):
    """
    This filters the minor noise nodes
    and added the userdefined nodes.
    """

    logger = logging.getLogger(__name__)
    logger.info('Setup filtering phase')

    def _device(g, n):
        if 'device' in g.node[n]:
            if tools.is_master(g.node[n]['device']):
                return True
        return False


    def _label(g, n):
        if 'label' in g.node[n]:
            if tools.is_master(g.node[n]['label']):
                return True
        return False

    g = ix.branches(g, gds)

    remove = list()
    for n in g.nodes():
        if _device(g, n) or _label(g, n):
            pass
        else:
            if len([i for i in g[n]]) < 3:
                remove.append(n)
    g.remove_nodes_from(remove)

    return g


def series_nodes(g):
    """
    Relabel all series connected nodes, even if they are masternodes.
    """

    logger = logging.getLogger(__name__)
    logger.info('Series filtering phase')

    def _filter_node(g, n):
        if 'label' in g.node[n]:
            label = g.node[n]['label']
            if isinstance(label, mn.Shunt):
                return True
            elif isinstance(label, mn.Ground):
                return True
            elif isinstance(label, mn.Capacitor):
                return True
        return False

    def _series_nodes(g):
        for n in g.nodes():
            if len([i for i in g[n]]) == 2:
                if _filter_node(g, n) is False:
                    g.node[n]['label'] = mn.Unique('series', 
                                                   g.node[n]['pos'])
            elif len([i for i in g[n]]) > 2:
                if isinstance(g.node[n]['poly'], mn.Inductor):
                    g.node[n]['label'] = mn.UserNode('usernode', 
                                                     g.node[n]['pos'])
        return g

    def _remove_series_nodes(g):
        remove = list()
        
        for n in g.nodes():
            if 'label' in g.node[n]:
                label = g.node[n]['label']
                if isinstance(label, mn.Remove):
                    if len([i for i in g[n]]) == 2:
                        e = tuple([i for i in g[n]])
                        g.add_edge(*e, label=None)
                        remove.append(n)
            
        g.remove_nodes_from(remove)
                
        return g

    g = _series_nodes(g)

    g = ix.branches(g, 0)

    g = combine_nodes(g)

    g = _remove_series_nodes(g)

    return g


def combine_nodes(g):
    """ Combine all nodes of the same type into one node. """

    def partition_nodes(u, v):
        if ('device' in g.node[u]) and ('device' in g.node[v]):
            if g.node[u]['device'].id == g.node[v]['device'].id:
                return True

        if ('label' in g.node[u]) and ('label' in g.node[v]):
            if g.node[u]['label'].id == g.node[v]['label'].id:
                return True

        if ('label' not in g.node[u]) and ('label' not in g.node[v]):
            if g.node[u]['poly'].id == g.node[v]['poly'].id:
                return True

    def sub_nodes(b):
        S = g.subgraph(b)

        device = nx.get_node_attributes(S, 'device')
        label = nx.get_node_attributes(S, 'label')
        poly = nx.get_node_attributes(S, 'poly')
        center = nx.get_node_attributes(S, 'pos')

        sub_pos = list()
        for key, value in center.items():
            sub_pos = [value[0], value[1]]

        return dict(device=device, label=label, poly=poly, pos=sub_pos)

    Q = nx.quotient_graph(g, partition_nodes, node_data=sub_nodes)

    Device = nx.get_node_attributes(Q, 'device')
    Pos = nx.get_node_attributes(Q, 'pos')
    Label = nx.get_node_attributes(Q, 'label')
    Polygon = nx.get_node_attributes(Q, 'poly')

    Edges = nx.get_edge_attributes(Q, 'weight')

    g1 = nx.Graph()

    for key, value in Edges.items():
        n1, n2 = list(key[0]), list(key[1])
        g1.add_edge(n1[0], n2[0])

    for n in g1.nodes():
        for key, value in Pos.items():
            if n == list(key)[0]:
                g1.node[n]['pos'] = [value[0], value[1]]

        for key, value in Label.items():
            if n == list(key)[0]:
                if n in value:
                    g1.node[n]['label'] = value[n]

        for key, value in Polygon.items():
            if n == list(key)[0]:
                g1.node[n]['poly'] = value[n]

        for key, value in Device.items():
            if n == list(key)[0]:
                if n in value:
                    g1.node[n]['device'] = value[n]
    return g1

