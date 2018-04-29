import itertools
import collections
import ast
import astor
import time
class Node:
    def __init__(self,node_input,node_type,index):
        self.data = node_input
        self.type = node_type
        self.in_data = []
        self.out_data = []
        self.calls = []
        self.index = index
        self.parents = []
        self.children = []
        self.value = None
        self.time = None
        self.optional = False
        if self.type == 'stmt':
            self.var_data(node_input)
            self.body = astor.to_source(node_input)
        elif self.type == 'func':
            self.get_arguments(list(ast.iter_fields(node_input))[1][1])
            self.get_funcname(list(ast.iter_fields(node_input)))
            self.body = astor.to_source(node_input)
            self.optional = True
        elif self.type == "hard_var":
            self.body = node_input
            

        elif self.type == "hard_var_optional":
            self.body = node_input
            self.type = "hard_var"
            self.optional = True
        else:
            self.raw_var_data(node_input)
            self.body = astor.to_source(node_input)
            
        self.out_data = list(set(self.out_data))
    def get_funcname(self,node_input):
        if node_input[0][0] == 'name':
            self.out_data.append(node_input[0][1])
    def get_arguments(self,node_input):
        if list(ast.iter_child_nodes(node_input)) == []:
            self.in_data.append(list(ast.iter_fields(node_input))[0][1])
        else:
            for node in ast.iter_child_nodes(node_input):
                self.get_arguments(node)
    def add_parent(self,node):
        self.parents.append(node)
    def add_child(self,node):
        self.children.append(node)
        

        
    def raw_var_data(self,astree):
        for node in ast.iter_child_nodes(astree):
            try:
                if isinstance(list(ast.iter_fields(node))[1][1], ast.Store):
                    self.out_data.append(list(ast.iter_fields(node))[0][1])
                elif isinstance(list(ast.iter_fields(node))[1][1], ast.Load):
                    in_dat = list(ast.iter_fields(node))[0][1]
                    if in_dat[0] != "[":
                        self.in_data.append(list(ast.iter_fields(node))[0][1])
            except:
                self.raw_var_data(node)
                continue
            self.raw_var_data(node)
                    
            
    def var_data(self,astree,check=0):
        for node in ast.iter_child_nodes(astree):
            if isinstance(node, ast.Call):
                c_node =list(ast.iter_fields(node))[0][1]
                if isinstance(c_node,ast.Attribute):
                     self.var_data(c_node, check=1)
                else:
                    self.in_data.append(list(ast.iter_fields(c_node))[0][1])
                for new_node in list(ast.iter_fields(node))[1][1]:
                    if isinstance(new_node, ast.Name):
                        self.in_data.append(list(ast.iter_fields(new_node))[0][1])
                    else:
                        self.in_data.append(new_node)
            else:
                try:
                    if isinstance(list(ast.iter_fields(node))[1][1], ast.Store):
                            
                        self.out_data.append(list(ast.iter_fields(node))[0][1])
                    elif isinstance(list(ast.iter_fields(node))[1][1], ast.Load):
                        if check == 0:
                            self.in_data.append(list(ast.iter_fields(node))[0][1])
                        else:
                            self.in_data.append(list(ast.iter_fields(node))[0][1])
                            self.out_data.append(list(ast.iter_fields(node))[0][1])
                except:
                    self.var_data(node)
                    continue
                self.var_data(node)