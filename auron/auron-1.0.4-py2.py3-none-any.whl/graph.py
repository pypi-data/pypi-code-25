import numpy as np
import networkx as nx

from auron import tools
from auron import filters

from yuna import masternodes as mn


def check_terminal_duplicates(edgelabels):
    duplicates = defaultdict(list)

    for i, item in enumerate(edgelabels):
        duplicates[item].append(i)

    duplicates = {k:v for k, v in duplicates.items() if len(v) > 1}

    for key, value in duplicates.items():
        if key is not None:
            if len(value) > 1:
                raise('Terminal duplicates!')


def update_adjacent_matrix(g, t1, adj_mat, v1, v2):
    """
    Label the triangle that contains terminal layers.

    Parameters
    ----------
    g : NetworkX graph object
        Graph nodes are updated with labels
    n : int
        Node id in the graph
    label : gdspy object
        Label objec from the gdspy library that contains the label text and position.
    poly : list
        Points of the triangle polygon.

    Returns
    -------
    g : NetworkX graph object
        Updated graph with labels are returned.
    """

    if (adj_mat[v1][v2] != 0):
        t2 = adj_mat[v1][v2] - 1
        g.add_edge(t1, t2, label=None)
    else:
        adj_mat[v1][v2] = t1 + 1
        adj_mat[v2][v1] = t1 + 1


def create_graph_edges(g, mesh):
    """
    Label the triangle that contains terminal layers.

    Parameters
    ----------
    g : NetworkX graph object
        Graph nodes are updated with labels
    n : int
        Node id in the graph
    label : gdspy object
        Label objec from the gdspy library that contains the label text and position.
    poly : list
        Points of the triangle polygon.

    Returns
    -------
    g : NetworkX graph object
        Updated graph with labels are returned.
    """
    """
        Parameters
        ----------
        adjacent_matrix : nparray
            See which edges are connected through
            triangles. Save triangle id to which the
            edge exists.

        triangles : nparray
            Array containing the node ids of the 3
            vertices of the triangle.

        Notes
        -----
        * From triangles:
            tri --> [v1, v2, v3]
            edge --> 1-2, 2-3, 1-3

        Algorithm
        ---------
        * Loop through every triangle and its edges.
        * Save the triangle id in the adjacent_matrix
        with index of (v1, v2).
    """

    ll = len(mesh['points'])
    A = np.zeros((ll, ll), dtype=np.int64)

    for i, tri in enumerate(mesh['cells']['triangle']):
        v1, v2, v3 = tri[0], tri[1], tri[2]

        update_adjacent_matrix(g, i, A, v1, v2)
        update_adjacent_matrix(g, i, A, v1, v3)
        update_adjacent_matrix(g, i, A, v2, v3)

    return g


def position_graph_nodes(g, mesh):
    """
    Label the triangle that contains terminal layers.

    Parameters
    ----------
    g : NetworkX graph object
        Graph nodes are updated with labels
    n : int
        Node id in the graph
    label : gdspy object
        Label objec from the gdspy library that contains the label text and position.
    poly : list
        Points of the triangle polygon.

    Returns
    -------
    g : NetworkX graph object
        Updated graph with labels are returned.
    """

    for n, tri in enumerate(mesh['cells']['triangle']):
        pp = mesh['points']
        n1, n2, n3 = pp[tri[0]], pp[tri[1]], pp[tri[2]]

        sum_x = 100e6*(n1[0] + n2[0] + n3[0]) / 3.0
        sum_y = 100e6*(n1[1] + n2[1] + n3[1]) / 3.0

        g.nodes[n]['vertex'] = tri
        g.nodes[n]['pos'] = [sum_x, sum_y]

    return g
