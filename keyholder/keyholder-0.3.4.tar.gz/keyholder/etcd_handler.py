from interface import implements
from keyHandler import keyHandler

import etcd


class etcd_handler(implements(keyHandler)):
    conn = None
    host = ""
    port = 0
    logging = None
    state = ""

    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.conn = etcd.Client(host=host, port=port, allow_redirect=True)

    def create(self, path):
        self.conn.write(path, 'testpath', prevExist=False)

    def ensure_path(self, path):
        try:
            self.create(path)
        except etcd.EtcdAlreadyExist:
            pass #if we catch this exception - it is ok

    def exists(self, node):
        try:
            tmp = self.conn.read(node)
            return True
        except etcd.EtcdKeyNotFound:
            return False
        except etcd.EtcdNotDir:
            return True

    def get_node_data(self, node):
        try:
            return [self.conn.read(node).value, "CONNECTED"]
        except etcd.EtcdKeyNotFound:
            return [None, "CONNECTED"]

    def set_node_data(self, node, data):
        self.conn.write(node,data)

    def delete_node(self, node, isrecursive):
        self.conn.delete(node, isrecursive)