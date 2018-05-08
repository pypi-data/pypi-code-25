from interface import Interface

class keyHandler(Interface):

    def __init__(self,host,port):
        pass

    def create(self,path):
        pass


    def ensure_path(self,path):
        pass


    def exists(self,node):
        pass


    def get_node_data(self,node):
        pass


    def set_node_data(self,node,data):
        pass


    def delete_node(self,node,isrecursive):
        pass
