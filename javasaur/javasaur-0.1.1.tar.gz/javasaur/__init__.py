import javalang
from . import node

def get_class(data):
    class_node = node.Class()
    tree = javalang.parse.parse(data)
    class_node.package_name = javalang.parse.parse(tree.package.name)
    class_node.name = tree.types[0].name
    class_node.tree = tree
    #TODO: Initialize members and methods list
    return class_node.name