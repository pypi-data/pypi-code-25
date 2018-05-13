# -*- encoding: utf-8 -*-
##############################################################################
#
#    Acrisel LTD
#    Copyright (C) 2008- Acrisel (acrisel.com) . All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
'''
Created on Jun 29, 2016

@author: arnon
'''
import pprint
import json
from copy import deepcopy

class Node(object):
    def __init__(self, name, value=None):
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

    @value.getter
    def value(self):
        return self._value
        
    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return repr(self.name) + ' : ' + repr(self.value)

    def __str__(self):
        return repr(self)


class Edge(object):
    def __init__(self, node1, node2):
        self.source = node1
        self.target = node2

    def from_node(self):
        return self.source

    def to_node(self):
        return self.target


class DiGraph(object):
    def __init__(self, nodes=None):
        self.nodes = nodes if nodes else dict()
        # self.dfs_weights=dict()

    Node = Node

    def add_node(self, node):
        found = self.nodes.get(node.name)
        if not found:
            result = dict([('node', node),
                           ('nexts', list()),
                           ('prevs', list())])
            self.nodes[node.name] = result
        return found is None
    
    def node_value(self, name):
        #print('Type:',type(self.nodes[name]['node']))
        return self.nodes[name]['node'].value

    
    def prevs(self,node):
        props = self.nodes.get(node.name)
        return props['prevs']
    
    def prevs_by_name(self,node_name):
        props = self.nodes.get(node_name)
        return self.prevs(props['node'])
        
    def add_edge(self, from_node, *to_nodes):
        fname = from_node.name
        fnode = self.nodes.get(fname)
        if not fnode:
            raise Exception("EdgeError: From-Node {} not in tree".format(from_node.name))
            #fnode=self.Node(from_node)
            #self.add_node(from_node)

        nexts = fnode['nexts']
        for node in to_nodes:
            tname = node.name
            tnode = self.nodes.get(node.name)
            if not tnode: 
                raise Exception("EdgeError: To-Node {} not in tree".format(node.name))

            if tname not in nexts:
                nexts.append(tname)
            prevs = tnode['prevs']
            if fname not in prevs:
                prevs.append(fname)
            #print('Added Edge:', from_node, node)
    
    def add_edge_by_name(self,from_name,*to_name):
        from_node=self.nodes.get(from_name)
        to_node=[self.nodes[name]['node'] for name in to_name]
        self.add_edge(from_node['node'],*to_node)
            
        
    def del_edge(self, from_node, *to_nodes):
        fname = from_node.name
        fnode = self.nodes.get(fname)
        nexts = fnode['nexts']
        for node in to_nodes:
            tname = node.name
            try: 
                nexts.remove(tname)
            except Exception: 
                pass

            tnode = self.nodes.get(tname)
            prevs = tnode['prevs']
            try:
                prevs.remove(fname)
            except:
                pass

    def del_node(self, node):
        dname = node.name
        dnode = self.nodes.get(dname)
        nexts = dnode['nexts']
        for tname in nexts:
            tnode = self.nodes.get(tname)
            prevs = tnode['prevs']
            try:
                prevs.remove(dname)
            except Exception:
                pass

        prevs = dnode['prevs']
        for fname in prevs:
            fnode = self.nodes.get(fname)
            nexts = fnode['nexts']
            try:
                nexts.remove(dname)
            except Exception:
                pass
        del self.nodes[dname]

    def _dfs(self, node_name, weights):
        props = self.nodes[node_name]
        try:
            for name in props['nexts']:
                if name not in weights.keys():
                    self._dfs(name, weights)
            weight = 1 + max([weights[name] for name in props['nexts']])
        except Exception:
            weight = 1
        weights[node_name] = weight

    def __len__(self):
        return len(self.nodes)

    def dfs(self, reverse=False):
        ''' Node iterator sorted depth first '''
        weights = dict()
        for node_name, props in self.nodes.items():
            if node_name not in weights.keys():
                self._dfs(node_name, weights)
        for name in sorted(weights.keys(), key=lambda x: weights[x], reverse = not reverse):
            yield self.nodes[name]['node']
    
    def roots(self):
        ''' Find independent nodes
            Return list of nodes with no previous nodes '''
        ans = [name for name,node in self.nodes.items() if not node['prevs']]
        return ans      
        
    def _ddfs(self, weights,graph_clone,roots,max_weight=0):
        for root in roots:
            weights[root] = max_weight
            ''' Get node object from dictionary of nodes and remove it from graph'''
            props = graph_clone.nodes[root]
            graph_clone.del_node(props['node'])
        
        roots = graph_clone.roots()
        if roots:
            self._ddfs(weights, graph_clone, roots, max_weight-1)


    def ddfs(self, reverse=False):
        ''' Node iterator sorted dependent depth first search
            The function returns nodes in the order of dependency. 
            First root nodes, then nodes with no incoming edges after removal of roots, ..... 
        '''
        weights = dict()
        graph_clone = deepcopy(self)
        roots = self.roots()
        self._ddfs(weights,graph_clone,roots)
        
        for name in sorted(weights.keys(), key=lambda x: weights[x], reverse = not reverse):
            yield self.nodes[name]['node']

    def __str__(self):
        return pprint.pformat(self.nodes)

    def to_file(self, fp):
        json.dump(self.nodes, fp)

    @classmethod
    def from_file(cls, fp):
        try:
            nodes = json.load(fp)
        except Exception:
            return None
        else:
            return cls(nodes)


if __name__ == '__main__':
    g = DiGraph()

    a = g.Node(('a', 1), 35)
    b = g.Node(('b', 2), 46)
    c = g.Node(('c', 3), 78)
    d = g.Node(('d', 4), 89)
    e = g.Node(('e', 1), 35)
    
    g.add_node(a)
    g.add_node(b)
    g.add_node(c)
    g.add_node(d)
    g.add_node(e)
    
    g.add_edge_by_name(('a',1), ('b',2))
    g.add_edge(b, c)
    g.add_edge(e, d)
    g.add_edge(c, d)

    print('Resulting graph:', g)

    #g.del_node(d)
    #print(g)
    print('Graph nodes:')
    for node in g.dfs(reverse=True):
        print(node.name, node.value)
    print('Graph roots:', g.roots())
    print('DDFS Nodes iterator:',list(g.ddfs()))
    #print('Original graph:',g)
    print('Edges to d:',g.prevs_by_name(('d',4)))
    print("Retrieve Node's %s value by node name. Value:%s" % (('d',4),g.node_value(('d', 4))))
    