from ..core import Graph


class Dataset(Graph):
    def __init__(self,
                 name,
                 tensors=None,
                 subgraphs=None,
                 graph_info=None,
                 config=None):
        super.__init__(name, tensors, subgraphs, graph_info, config)


class FromHDF5(Graph):
    def __init__(self, name, h5dataset):
        pass