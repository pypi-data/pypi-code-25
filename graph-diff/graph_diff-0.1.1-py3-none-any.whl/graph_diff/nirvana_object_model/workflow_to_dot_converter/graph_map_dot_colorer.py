from abc import ABC, abstractmethod

from graph_diff.nirvana_object_model.workflow import Block


class GraphDotColorer(ABC):
    """Interface for graph workflow colorer"""

    @abstractmethod
    def color_of_block(self,
                       block: Block,
                       number: int): pass

    @abstractmethod
    def color_data_connection(self,
                              from_block: Block,
                              from_number: int,
                              output_nest: str,
                              to_block: Block,
                              to_number: int,
                              input_nest: str): pass

    @abstractmethod
    def color_exc_connection(self,
                             from_block: Block,
                             from_number: int,
                             to_block: Block,
                             to_number: int): pass


class StandardGraphDotColorer(GraphDotColorer):
    """Standard realization of GraphDotColorer: colors all elements in standard color"""

    STANDARD_COLOR = 'black'

    def color_of_block(self,
                       block: Block,
                       number: int): return self.STANDARD_COLOR

    def color_data_connection(self,
                              from_block: Block,
                              from_number: int,
                              output_nest: str,
                              to_block: Block,
                              to_number: int,
                              input_nest: str): return self.STANDARD_COLOR

    def color_exc_connection(self,
                             from_block: Block,
                             from_number: int,
                             to_block: Block,
                             to_number: int): return self.STANDARD_COLOR


class GraphMapDotColorer(GraphDotColorer):
    """Realization of GraphDotColorer that is interface over three dictionaries"""

    def __init__(self, block_colors, data_connection_colors, exc_connection_colors):
        self._block_colors = block_colors
        self._data_connection_colors = data_connection_colors
        self._exc_connection_colors = exc_connection_colors

    def color_of_block(self,
                       block: Block,
                       number: int):
        return self._block_colors[block, number]

    def color_data_connection(self,
                              from_block: Block,
                              from_number: int,
                              output_nest: str,
                              to_block: Block,
                              to_number: int,
                              input_nest: str):
        return self._data_connection_colors[from_block, from_number, output_nest, to_block, to_number, input_nest]

    def color_exc_connection(self,
                             from_block: Block,
                             from_number: int,
                             to_block: Block,
                             to_number: int):
        return self._exc_connection_colors[from_block, from_number, to_block, to_number]
