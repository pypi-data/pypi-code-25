import pydot

from graph_diff.nirvana_object_model.workflow import Block, Workflow
from .graph_map_dot_colorer import StandardGraphDotColorer, GraphDotColorer


class WorkflowToDotConverter:
    BY_EXC = "by_exc"

    def __init__(self, separator='',
                 graph_type='digraph',
                 node_shape='record',
                 general_color='black',
                 general_style='"rounded,filled"',
                 changed_style='"rounded,filled,bold"'):
        """
        :param separator: separator if needed
        (it is often needed to print several workflows together).
        """

        self._separator = separator
        self.graph_type = graph_type
        self.node_shape = node_shape
        self.general_color = general_color
        self.general_style = general_style
        self.changed_style = changed_style

    def __block_id_generator(self, block: Block, addition='') -> str:
        """
        Generates unique string id for a block.

        :param block:       block to get id
        :param addition:    addition if needed
        :return:            string representation
        """

        res = block.operation.operation_id + str(hash(block.options)) + '_' + addition + self._separator
        return res

    @staticmethod
    def __block_body_printer(block: Block) -> str:
        """
        Transforms block to string representation of node in pydot

        :param block:   block to print
        :return:        string to be inserted as node to pydot.Dot
        """

        outputs = block.operation.outputs
        outputs = zip(outputs, outputs)
        outputs = '|'.join(['<o' + a + '>' + b for a, b in outputs])
        inputs = block.operation.inputs
        inputs = zip(inputs, inputs)
        inputs = '|'.join(['<i' + a + '>' + b for a, b in inputs])

        return '{ {' + inputs + '} | ' + '"' + block.operation.operation_id + '"' + ' | {' + outputs + '}}'

    def __edge_node_conversion(self, block: Block, num: int, nest: str, where: str = '') -> str:
        """
        Gets pydot representation of connection in workflow.

        :param block:   block where connection goes from
        :param num:     number of the block
        :param nest:    nest via connection goes (may be by_exc)
        :param where:   string where the connection goes
        :return:        string representation of connection in pydot format
        """

        return '"' + self.__block_id_generator(block, str(num)) + '"' + ':' + where + nest

    def convert_workflow(self,
                         workflow: Workflow,
                         colors: GraphDotColorer = StandardGraphDotColorer()) -> pydot.Dot:
        """
        Convert workflow to pydot.Dot.
        Elements of workflow will be colored with colors defined in colors object.

        :param workflow:    workflow to transform
        :param colors:      colors for workflow elements
        :return:            pydot representation of workflow
        """
        dot = pydot.Dot(graph_type=self.graph_type)

        from collections import defaultdict
        number_of_blocks = defaultdict(int)
        for block in workflow:
            number_of_blocks[block] += 1
            color = str(hex(254 * 16 ** 4 + 255 * 16 ** 2 + 241))[2:]
            style = self.general_style \
                if colors.color_of_block(block, number_of_blocks[block]) == self.general_color \
                else self.changed_style

            node = pydot.Node(self.__block_id_generator(block, addition=str(number_of_blocks[block])),
                              label=self.__block_body_printer(block),
                              shape=self.node_shape,
                              color=colors.color_of_block(block, number_of_blocks[block]),
                              style=style,
                              fillcolor='#' + color)

            dot.add_node(node)

        for (from_block, from_num, output_nest), a2 in workflow.items():
            for to_block, to_num, input_nest in a2:
                edge = pydot.Edge(src=self.__edge_node_conversion(from_block, from_num, output_nest, 'o'),
                                  dst=self.__edge_node_conversion(to_block, to_num, input_nest, 'i'),
                                  color=colors.color_data_connection(from_block, from_num, output_nest,
                                                                     to_block, to_num, input_nest))
                dot.add_edge(edge)

        for (from_block, from_num), a2 in workflow.items_by_exc():
            for to_block, to_num in a2:
                edge = pydot.Edge(src=self.__edge_node_conversion(from_block, from_num, self.BY_EXC),
                                  dst=self.__edge_node_conversion(to_block, to_num, self.BY_EXC),
                                  color=colors.color_exc_connection(from_block, from_num, to_block, to_num))
                dot.add_edge(edge)

        return dot


def print_together(*args, **kwargs) -> pydot.Dot:
    """
    Prints all workflow as one pydot.Dot object

    :param args:    workflows to print
    :param names:
    :return:
    """
    def dot_to_subgraph(graph: pydot.Dot, label: str) -> pydot.Cluster:
        graph_s = pydot.Cluster(label, label=label)
        # graph_s.set_edge_defaults(style='dashed', color='black', penwidth=1)
        graph_s.set_edge_defaults(color='black',
                                  penwidth=1)
        for node in graph.get_nodes():
            graph_s.add_node(node)
        for edge in graph.get_edges():
            graph_s.add_edge(edge)
        return graph_s

    res = pydot.Dot(splines=True)
    for name, workflow in zip(kwargs['names'], args):
        res.add_subgraph(dot_to_subgraph(workflow, name))
    return res
