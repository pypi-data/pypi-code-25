"""All implemented algorithms on trees in this library are plased here.
"""

from .structures import Tree, Node
from collections import deque

class CircleInTreeException(Exception):
    """This exception rases when the circle has detected
    during execution of any alg.
    Messages contain related node.
    """

    def __init__(self, node):

        message = "{} detected twice".format(str(node))
        super(CircleInTreeException, self).__init__(message)


def df_traversal(tree):
    """DFS traversal alg.
    Parameters
    ----------
    tree : Tree

    Returns
    -------
    deque([ [path1], [path2] ])
        deque of paths, path - list that contains the nodes of a path.

    Exceptions
    -------
    CircleInTreeException
        rases when there is a circle in a graph.
    """

    ways = deque([])

    root_node = tree.root_node
    curent_path = deque([ [root_node,0] ])

    while len(curent_path):

        last_path_entry = curent_path[-1]
        curent_node, next_cild_inx = last_path_entry


        if not len(curent_node.connections):
            #curent_node is a leave node
            ways.append([ node for node, it in curent_path ] )
            #go back
            curent_path.pop()

        elif len(curent_node.connections) ==  next_cild_inx:
            #there isn't more cildren nodes
            #go back
            curent_path.pop()

        else:
            #there is an avaliable next cildren node
            #go to the next cildren, make it curent
            next_cild_node = curent_node.connections[next_cild_inx]

            #check for circles in path
            if len([ 1 for node, inx  in curent_path if node == next_cild_node ]):
                raise CircleInTreeException(next_cild_node)

            curent_path.append( [next_cild_node,0] )

            last_path_entry[1] += 1


    return ways
