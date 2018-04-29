import itertools
import collections
import ast
import astor
class FragmentGenerator:
    
    def __init__(self,node_data):
        self.data = node_data
#        for node in node_data:
#            print("xxxxxxxxxx")
#            print(node.body)
#            print("xxxxxxxxxx")
#            for p in node.parents:
#                print("parent")
#                print(p.body)
#            print("\n")
#            for c in node.children:
#                print('child')
#                print(c.body)
#            print("\n\n\n\n")
        self.extract()
    def frag_print(self,fragment):
        for node in fragment:
            print(node.body)
        print("-----------------")
        print("-----------------")
    def extract(self):
        self.FragData = []
        self.JunctionData = {}
        def flatten(x):
            if isinstance(x, collections.Iterable):
                return [a for i in x for a in flatten(i)]
            else:
                return [x]
        def initiate(node,c_frag = None):
            if len(node.parents) <= 1 and len(node.children) > 0:
                for kid in node.children:
                    local_fragments = []
                    if len(kid.parents) > 1:
                        if c_frag == None:
                            c_frag = [[node]]
                        else:
                            c_frag.append([node])
                        initiate(kid,c_frag = c_frag)
                        return
                    if c_frag != None:
                        for fragment in c_frag:
                            fragment.append(kid)
                            local_fragments.append(fragment)
                            self.FragData.append(fragment)
#                            self.frag_print(fragment)
                    local_fragments.append([node,kid])

                    self.FragData.append([node,kid])
#                    self.frag_print([node,kid])
                    initiate(kid,c_frag = local_fragments)
            elif len(node.parents) > 1:
                if c_frag != None:
#                    input("lol")
#                    for frag in c_frag:
#                        for llot in frag:
#                            print(llot.body)
#                        print("====")
#                    input("lol_end")
                    if node in self.JunctionData.keys():
                        fragment = self.JunctionData[node]
                        fragment.append(c_frag)
                        self.JunctionData[node] = fragment
                    else:
                        self.JunctionData[node] = [c_frag]
            return
        
#                
#            
        for node in self.data:
            if node.type == 'hard_var':
                initiate(node.children[0])
            elif node.type == 'func':
                for child in node.children:
                    self.FragData.append([node,child])
#                    self.frag_print([node,child])
                    initiate(child,c_frag = [[node,child]])
        while len(self.JunctionData) > 0:
            local_fragments = []
            
            junc_node = list(self.JunctionData.keys())[0]
#            input(junc_node.body)
            frag_collection = self.JunctionData[junc_node]
#            input(junc_node.body)
#            for sect in frag_collection:
#                for fragment in sect:
#                    for node in fragment:
#                        print(node.body)
#                    print("=========")
#                print("++++++++++++")
#            input()
            c_frag = list(itertools.product(*frag_collection))
            for section in c_frag:
                section = list(set(flatten(section)))
                section.append(junc_node)
                local_fragments.append(section)
                local_fragments.append([junc_node])
                if section not in self.FragData:
                    self.FragData.append(section)
#                    self.frag_print(section)
            if len(junc_node.children) > 0:
                for kid in junc_node.children:
                    for fragment in local_fragments:
                        fragment.append(kid)
                        if fragment not in self.FragData:
                            self.FragData.append(fragment)
                    initiate(kid,local_fragments)
#            else:
#                input('lol')
#                for fragment in local_fragments:
#                    for frag in fragment:
#                        print(frag.body)
#                    print("xxxxxxx")
#                input('lol')
            self.JunctionData.pop(junc_node)
#        print(len(self.FragData))