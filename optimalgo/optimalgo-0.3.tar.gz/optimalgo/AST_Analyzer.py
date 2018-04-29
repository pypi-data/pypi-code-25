import itertools
import collections
import ast
import astor
from .Node import *
class AST_Analyzer:
    def __init__(self,code_input):
        self.AST = ast.parse(code_input)
        self.NodeData = []
        self.blocks = ["<class '_ast.FunctionDef'>","<class '_ast.If'>","<class '_ast.For'>","<class '_ast.While'>"]
        self.analyze_1(self.AST)
        self.tree_gen(self.NodeData)
#        print(ast.dump(self.AST))
#        for i in self.NodeData:
#            print(i.in_data)
#            print(i.out_data)
#            print(i.body)
#            print(i.calls)
#            print("\n\n")
        
    def analyze_1(self,astree):
        counter = 1
        for node in ast.iter_child_nodes(astree):
            if str(type(node)) in self.blocks:
                if str(type(node)) == self.blocks[0]:
                    self.NodeData.append(Node(node,'func',counter))
                else:
                    self.NodeData.append(Node(node,'block',counter))
            else:
                self.NodeData.append(Node(node,'stmt',counter))
            counter+=1
    def tree_gen(self,node_data):
        last_stored = {}
        last_accessed = {}
        for node in node_data:
            
            parents = []
            for var in node.in_data:
                if isinstance(var,str):
                    if var in last_stored.keys():
                        if last_stored[var] not in node.parents and node != last_stored[var]:
                            node.add_parent(last_stored[var])
                elif len(node.in_data) == 1:
                    new_node = Node(var,'hard_var',None)
                    new_node.add_child(node)
                    self.NodeData.append(new_node)
                    if new_node not in node.parents:
                        node.add_parent(new_node)
                else:
                    new_node = Node(var,'hard_var_optional',None)
                    new_node.add_child(node)
                    self.NodeData.append(new_node)
                    if new_node not in node.parents:
                        node.add_parent(new_node)
            for var in node.out_data:
                last_stored[var] = node
            for parent in node.parents:
                if node not in parent.children:
                    parent.add_child(node)
                