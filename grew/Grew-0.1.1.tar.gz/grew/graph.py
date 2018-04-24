"""
Grew module : anything you want to talk about graphs
Graphs are represented either by a dict (called dict-graph),
or by an str (str-graph).
"""
import os.path
import re
import copy
import tempfile
import json

import utils
import network
import ast
import grew

''' interfaces'''

def graph2dot(graph):
    """
    Transformation of a graph to a graphviz string
    :param graph: a graph (dict)
    :return: string
    """
    s = 'graph G{\n'
    for n in graph:
        s += '%s [label="%s"]\n' % (n, graph[n][0])
    for n in graph:
        for (nid, lab) in graph[n][1]:
            s += '%s->%s[label="%s"]\n' % (n, nid, lab)
    return s + '}'

def graph(data=None):
    """
    :param data: either a list of string,
                 or a string in GREW format
                 or a filename in GREW format
                 or an other graph
    :return: a graph
   """
    if not data:
        return dict()
    if isinstance(data, list):
        # builds a flat ordered (using list order) graph
        return {utils.float2id(float(i)): (data[i], []) for i in range(len(data))}
    elif isinstance(data, str):
        # build from a JSON string
        return json.loads(data)
    elif isinstance(data,dict):
        # copy an existing graph
        return copy.deepcopy(data)
    else:
        raise grew.GrewError('Library call error')



def add_node(g, s, a):
    """
    Add a node s labeled a in graph g
    """
    g[s] = (a, []) # ERROR

def add_edge(gr, source, label, target):
    """
    Add an edge from [source] to [target] labeled [label] within [gr]
    :param gr: the graph
    :param source: the source node id
    :param label: the label of edge between [source] and [target]
    :param target: the target node id
    :return:
    """
    if source not in gr or target not in gr:
        raise KeyError("Add_edge")
    else:
        succs = gr[source][1]
        if not (label, target) in succs:
            succs.append((label, target))


def insert_before(gr, label, pivot):
    """
    Add a new node to the ordered graph
    :param gr: an ordered graph
    :param label: the label of the new node
    :param pivot: the new node will be put just before the node [pivot]
    :return: the id of the new node
    """
    leftid = utils.glb(gr, pivot)
    nid = utils.mid(leftid, pivot) if leftid else utils.left(pivot)
    gr[nid] = ('label="%s"'%(label), [])
    return nid

def insert_after(gr, label, pivot):
    """
    Add a new node to the ordered graph
    :param gr: an ordered graph
    :param label: the label of the new node
    :param pivot: the new node will be put just after the node [pivot]
    :return: the id of the new node
    """
    rightid = utils.lub(gr, pivot)
    nid = utils.mid(rightid, pivot) if rightid else utils.right(pivot)
    gr[nid] = ('label="%s"'%(label), [])
    return nid


_canvas = None
def draw(gr,format=None):
    global _canvas
    """Opens a window with the graph."""

    image = grew.dot_graph(gr)

    if not _canvas:
        import tkinter
        from tkinter import Tk, Canvas, PhotoImage, NW
        app = Tk()
        _canvas = Canvas(app, width=900, height=500)
        _canvas.pack()
        pic = PhotoImage(file=image)
        _canvas.create_image(0, 0, anchor=NW, image=pic)
        app.mainloop()