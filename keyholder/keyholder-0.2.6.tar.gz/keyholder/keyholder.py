from handlers.zoo_handler import *

class keyholder:
    host = ""
    port = 0
    type = ""
    namespace = ""
    conn = None
    state = ""
    def __init__(self,namespace, type="zookeeper",host="127.0.0.1",port=2181):
        self.host = host
        self.port = port
        self.type = type
        self.namespace = namespace
        if (self.type == "zookeeper"):
            self.conn = zoo_handler(self.host, self.port)
            self.state = self.conn.state

    def create(self,path):
        self.conn.create(path)

    def ensure_path(self,path):
        self.conn.ensure_path(path)

    def exists(self,node):
        if (self.conn.exists(node) == None):
            return False
        return True

    def get_node_data(self,node):
        return self.conn.get_node_data(node)

    def set_node_data(self,node,data):
        self.conn.set_node_data(node,data)

    def delete_node(self,node,isrecursive):
        self.conn.delete_node(node,isrecursive)

