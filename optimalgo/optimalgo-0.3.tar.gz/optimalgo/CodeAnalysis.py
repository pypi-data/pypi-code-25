import itertools
import collections
import ast
import astor
from .AST_Analyzer import *
from .FragmentExecutor import *
from .FragmentGenerator import *
from .Fragment import *
class CodeAnalysis:
    def __init__(self,file):
        NodeData = AST_Analyzer(file).NodeData
        self.InstanceData = FragmentExecutor(NodeData).data
        Fragmentation = FragmentGenerator(self.InstanceData)
        self.FragmentData = Fragmentation.FragData
        self.block_recursion(self.InstanceData)
    def show_fragments(self):
        for fragment in self.FragmentData:
            for node in fragment:
                print(node.body)
            print("-_-_-_-_-_-_-_-_-_-_-_-_-_-_-")
    def show_instances(self):
        for node in self.InstanceData:
            print(node.body)
            print(node.value)
            print("######################")
    def block_recursion(self,data):
        for node in data:
            try:
                if node.type == 'func':
    #                print(node.body)
                    for caller in data:
                        if node.out_data[0] in caller.in_data:
                            arguments = []
                            for parent in caller.parents:
                                if parent == node:
                                    continue
                                else:
                                    arguments.append(parent.value)
                            break

                    block = list(ast.iter_fields(node.data))[2][1]
                    body = ""
                    for line in block[:-1]:
                        body += astor.to_source(line)
    #                body = astor.to_source(list(ast.iter_fields(node.data))[2][1])

                    arg_body = ""
                    for i,arg in enumerate(node.in_data):
                        try:
                            c_string = arg+"="+arguments[0][i]
                            arg_body+=c_string+"\n"
                        except:
                            continue
                    body = arg_body+body

                    block_object = CodeAnalysis(body)
                    self.FragmentData+=block_object.FragmentData
                    self.InstanceData+=block_object.InstanceData
                elif node.type == 'block' and list(ast.iter_fields(node.data))[0][0] == 'target':
                    body = ""
                    for sect in list(ast.iter_fields(node.data))[2][1]:
                        body+=astor.to_source(sect)+"\n"

                    arg_body = ""
                    for parent in node.parents:
                        for i,out_var in enumerate(parent.out_data):
                            try:
                                c_string = out_var+"="+parent.value[i]
                                arg_body+=c_string+"\n"
                            except:
                                continue
                    target = list(ast.iter_fields(list(ast.iter_fields(node.data))[0][1]))[0][1]
                    iterable_body = node.body[:node.body.index("\n")]
                    exec(arg_body)
                    exec(iterable_body+"\n    "+"it_var = "+target)
                    target_val = eval("it_var")
                    arg_body+=target+"="+str(target_val)+"\n"
                    body = arg_body+body
                    block_object = CodeAnalysis(body)
                    self.FragmentData+=block_object.FragmentData
                    self.InstanceData+=block_object.InstanceData
                elif node.type == 'block' and list(ast.iter_fields(node.data))[0][0] == 'test':
                    arg_body = ""
                    for parent in node.parents:
                        for i,out_var in enumerate(parent.out_data):
                            c_string = out_var+"="+parent.value[i]
                            arg_body+=c_string+"\n"

                    for block in list(ast.iter_fields(node.data))[1:]:
                        body = ""
                        for line in block[1]:
                            body+=astor.to_source(line)+"\n"  
                        body = arg_body+"\n"+body
                        self.FragmentData+=CodeAnalysis(body).FragmentData
                        self.InstanceData+=CodeAnalysis(body).InstanceData
            except:
                continue
    def fragment_io(self):
        io_data = []
        for fragment in self.FragmentData:
            frag_object = Fragment(fragment)
            if frag_object.status == True:
                io_data.append(frag_object)
        return(io_data)
    
    
#    
#    
#file = open('pa_2.py',"r").read()
#a = CodeAnalysis(file)
#io_data = a.fragment_io()
##
###print(len(io_data)) 
###input("start")
#for fragment in io_data:
##    print("FRAGMENT")
##    for node in fragment.nodes:
##        print(node.body)
##    print("---------------")
#    print(fragment.input_val, ": \t input")
#    print(fragment.optional_input, ": \t opt input")
#    print(fragment.output_val, ": \t output")
##    print(fragment.time,": \t Time")
##    print("==================\n\n")
