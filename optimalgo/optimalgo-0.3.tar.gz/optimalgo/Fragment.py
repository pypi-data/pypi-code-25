class Fragment:
    def __init__(self,frag):
        self.nodes = frag
        self.input_val = []
        self.optional_input = []
        self.output_val = None
        self.status = True
        self.time = 0
        self.get_input()
        self.get_output()
        if self.input_val == []:
            self.status = False
        
            
            
    def get_input(self):
#        for node in self.nodes:
#            print(node.body)
#        print("======@@@@@@@@@@@@@@")
        for node in self.nodes:
            try:
                self.time+=node.time
            except:
                self.time+=0
            for node_2 in node.parents:
                if node_2 not in self.nodes:
                    if node_2.type == "hard_var":
                        self.input_val+=node.value
                        continue
                    if node_2.optional == True:
                        self.optional_input+=node_2.value
                    else:
                        self.input_val+=node_2.value
    def get_output(self):
        max_node = None
        for node in self.nodes:
            if max_node == None:
                max_node = [node.value,node.data.lineno]
            elif node.data.lineno > max_node[1]:
                max_node = [node.value, node.data.lineno]
        self.output_val = max_node[0]