from graph_diff.graph import rnr_graph, lr_node, GraphWithRepetitiveNodesWithRoot
from graph_diff.graph_diff_algorithm import GraphMap
from graph_diff.nirvana_object_model.workflow import Block, Operation, Workflow
from graph_diff.nirvana_object_model.workflow_to_dot_converter import GraphMapDotColorer
from .workflow_to_graph_converter import WorkflowToGraphConverter


class SimpleWorkflowToGraphConverter(WorkflowToGraphConverter):
    """Simplest workflow to graph converter: every block is one node"""

    NEST_DIVIDER = "<n>"
    KEY_VALUE_DIVIDER = "<:>"
    KEY_VALUE_BLOCK_DIVIDER = "<;>"
    INPUT_DIVIDER = "<i>"
    OUTPUT_DIVIDER = "<o>"

    def __init__(self,
                 matched_color='black',
                 added_color='green3',
                 deleted_color='red'):
        """
        :param matched_color:   color for matched elements
        :param added_color:     color for added elements
        :param deleted_color:   color for deleted elements
        """

        self.matched_color = matched_color
        self.added_color = added_color
        self.deleted_color = deleted_color

    def block_id(self, block: Block):
        """
        Generates id for block.

        :param block:   block to transform
        :return:        string representation
        """

        return_list = [block.operation.operation_id,
                       self.KEY_VALUE_BLOCK_DIVIDER.join([key + self.KEY_VALUE_DIVIDER + value
                                                          for key, value in block.options]),
                       self.INPUT_DIVIDER.join(block.operation.inputs),
                       self.OUTPUT_DIVIDER.join(block.operation.outputs)]
        return self.NEST_DIVIDER.join(return_list)

    def get_block(self, node: GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode):
        """
        Reverses transformation from node to block.

        :param node:    node to transform
        :return:        original block
        """

        splitted = node.Label.split(self.NEST_DIVIDER)
        assert len(splitted) == 4
        operation_id, key_values, input_nests, output_nests = splitted[0], splitted[1], splitted[2], splitted[3]
        key_values = dict([tuple(key_value.split(self.KEY_VALUE_DIVIDER))
                           for key_value in key_values.split(self.KEY_VALUE_BLOCK_DIVIDER)]
                          if len(key_values) > 0 else [])
        return Block(operation=Operation(operation_id=operation_id,
                                         inputs=input_nests.split(self.INPUT_DIVIDER),
                                         outputs=output_nests.split(self.OUTPUT_DIVIDER)),
                     options=key_values)

    def convert(self, workflow: Workflow) -> GraphWithRepetitiveNodesWithRoot:
        """
        Converts workflow to graph.
        This transformation is not fully reversible.
        Kind of connection betwixt blocks will be lost.

        :param workflow:    workflow to convert
        :return:            converted graph
        """

        graph = rnr_graph()
        from collections import defaultdict
        number_of_blocks = defaultdict(int)

        for block in workflow:
            number_of_blocks[block] += 1
            graph.add_node(lr_node(self.block_id(block), number_of_blocks[block]))

        for (from_block, from_num, _), a2 in workflow.items():
            for to_block, to_num, _ in a2:
                graph.add_edge_exp(lr_node(self.block_id(from_block), from_num),
                                   lr_node(self.block_id(to_block), to_num))

        for (from_block, from_num), a2 in workflow.items_by_exc():
            for to_block, to_num in a2:
                graph.add_edge_exp(lr_node(self.block_id(from_block), from_num),
                                   lr_node(self.block_id(to_block), to_num))

        return graph

    def reverse_graph(self, graph: GraphWithRepetitiveNodesWithRoot) -> Workflow:
        """
        Reverse transformation from graph to worflow.
        Possibility of transformation must be guaranteed from outside.
        As this transformation is not fully reversible,
        if nodes (blocks) have edge between them this connection is considered
        connection by execution despite the origin.

        :param graph:   graph to reverse
        :return:        original workflow
        """

        workflow = Workflow()

        for node in graph:
            if node.Label != graph.ROOT:
                workflow.add_block(self.get_block(node))
        for from_node in graph:
            if from_node.Label != graph.ROOT:
                for to_node in graph.get_list_of_adjacent_nodes(from_node):
                    workflow.add_connection_by_execution(from_block=self.get_block(from_node),
                                                         from_number=from_node.Number,
                                                         to_block=self.get_block(to_node),
                                                         to_number=to_node.Number)

        return workflow

    def convert_graph_map(self, graph_map: GraphMap) -> (Workflow, GraphMapDotColorer):
        """
        Convert graph map to workflow and colorer object.

        :param graph_map:   graph map to be transformed
        :return:            composed workflow and colorer for it
        """

        workflow = Workflow()

        def construct_set(graph_map_sub_set):
            block_blank = set()

            for node in graph_map_sub_set:
                if node != GraphWithRepetitiveNodesWithRoot.ROOT:
                    block = self.get_block(node)
                    block_blank.add((block, node.Number))

            return [block for block, number in block_blank], \
                   {(b, n): i for i, (b, n) in enumerate(block_blank)}

        block_overlap_from_first, map_for_matched = construct_set(graph_map.get_node_overlap_from_first())
        blocks_in_1_not_in_2, map_for_deleted = construct_set(graph_map.get_nodes_in_1_not_in_2())
        blocks_in_2_not_in_1, map_for_added = construct_set(graph_map.get_nodes_in_2_not_in_1())

        matcher = {}
        for (block, number), i in map_for_matched.items():
            matcher[block, number, 1] = block_overlap_from_first[i]
        for (block, number), i in map_for_deleted.items():
            matcher[block, number, 1] = blocks_in_1_not_in_2[i]
        for (block, number), i in map_for_added.items():
            matcher[block, number, 2] = blocks_in_2_not_in_1[i]

        from collections import defaultdict
        blocks_nums = defaultdict(int)
        num_of_the_block = {}
        block_colors = {}
        for block in block_overlap_from_first:
            blocks_nums[block] += 1
            num_of_the_block[id(block)] = blocks_nums[block]
            block_colors[block, blocks_nums[block]] = 'black'
            workflow.add_block(block)
        for block in blocks_in_1_not_in_2:
            blocks_nums[block] += 1
            num_of_the_block[id(block)] = blocks_nums[block]
            block_colors[block, blocks_nums[block]] = 'red'
            workflow.add_block(block)
        for block in blocks_in_2_not_in_1:
            blocks_nums[block] += 1
            num_of_the_block[id(block)] = blocks_nums[block]
            block_colors[block, blocks_nums[block]] = 'green'
            workflow.add_block(block)

        data_connection_colors = {}
        exc_connection_colors = {}

        def add_set_of_edges(graph_map_edge_set,
                             graph_number,
                             color,
                             trans_graph_number,
                             transform_node=lambda x: x):
            for from_node, to_node in graph_map_edge_set:
                if transform_node(from_node).Number != 0:
                    from_node = transform_node(from_node)
                    from_graph_number = trans_graph_number
                else:
                    from_graph_number = graph_number

                if transform_node(to_node).Number != 0:
                    to_node = transform_node(to_node)
                    to_graph_number = trans_graph_number
                else:
                    to_graph_number = graph_number

                if from_node != GraphWithRepetitiveNodesWithRoot.ROOT:
                    from_block = self.get_block(from_node)
                    to_block = self.get_block(to_node)
                    from_block = matcher[from_block,
                                         from_node.Number,
                                         from_graph_number]
                    to_block = matcher[to_block,
                                       to_node.Number,
                                       to_graph_number]
                    workflow.add_connection_by_execution(from_block=from_block,
                                                         from_number=num_of_the_block[id(from_block)],
                                                         to_block=to_block,
                                                         to_number=num_of_the_block[id(to_block)])
                    exc_connection_colors[from_block,
                                          num_of_the_block[id(from_block)],
                                          to_block,
                                          num_of_the_block[id(to_block)]] = color

        # Constructing sets and setting colors
        add_set_of_edges(graph_map.get_edge_overlap_from_first(),
                         1, self.matched_color, 1)
        add_set_of_edges(graph_map.get_edges_in_1_not_in_2(),
                         1, self.deleted_color, 1)
        add_set_of_edges(graph_map.get_edges_in_2_not_in_1(),
                         2, self.added_color, 1,
                         graph_map.map_from_2)

        return workflow, GraphMapDotColorer(block_colors, data_connection_colors, exc_connection_colors)
