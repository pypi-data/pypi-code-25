class GraphWithRepetitiveNodesKeyError(Exception):
    """
    Exception within GraphWithRepetitiveNodes.
    Indicated that edge added explicitly
    contains node not added to the graph.
    """

    def __init__(self, message):
        self.message = message


class LabeledRepetitiveNodePositiveArgumentException(Exception):
    """
    Exception within GraphWithRepetitiveNodes.
    Indicated that one tries to set number of node as a negative number.
    """
    def __init__(self, message):
        self.message = message
