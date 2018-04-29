import itertools
import collections
import ast
import astor
import time
from .CodeAnalysis import *
from .Data_Match import *

class file:
    def __init__(self,filename, data=None):
        
        file = open(filename,"r").read()
        ndata = CodeAnalysis(file)
#        data.show_fragments()
#        data.show_instances()
        fragment_data = ndata.fragment_io()
        matches = Data_Match(fragment_data,data).matches
#        print(matches)
        for match in matches:
            for node in match[0].nodes:
                print(node.body)
            print("=======")
            print(match[1])
            print("\n\n\n")
        
class console:
    def __init__(self,data=None):
        
        input_1 = input("Enter Input: ")
        input_2 = input("Enter Output: ")
        input_1 = input_1.split("&")
        matches = Data_Match(["console",input_1,input_2],data).matches
        if len(matches) > 1:
            input_1 = input("Enter Input: ")
            input_2 = input("Enter Output: ")
            input_1 = input_1.split("&")
            matches_2 = Data_Match(["console",input_1,input_2],data).matches
            for i in matches:
                if i in matches_2:
                    print(i)
        elif len(matches) == 1:
            print(matches[0])

    


    
                

            
            
            
                
                

                
                
                


            
                


                    
                    
                
                

            
                    
            
            
        

                    
                    
    
    
