class GraphDoesNotContainMappedNodeException(Exception):
    """
    Exception to be thrown GraphMap.
    Indicates that node is mapped to nonexistent node.
    """

    def __init__(self,
                 error_list: list):
        self.message = 'There are unmatched nodes during GraphMap.construct_graph_map:\n' \
                       + '\n'.join('{} is not found in graph {}'.format(node, num) for node, num in error_list)
