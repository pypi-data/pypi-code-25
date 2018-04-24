from graph_diff.graph import rnr_graph, lr_node, GraphWithRepetitiveNodesWithRoot
from graph_diff.graph_diff_algorithm import GraphMap
from graph_diff.nirvana_object_model.workflow import Block, Operation, Workflow
from graph_diff.nirvana_object_model.workflow_to_dot_converter import GraphMapDotColorer, GraphDotColorer
from .workflow_to_graph_converter import WorkflowToGraphConverter


class CompleteWorkflowToGraphConverter(WorkflowToGraphConverter):
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

    def block_id(self, block: Block) -> str:
        """
        Generates unique identifier by block.

        :param block:   block to identify
        :return:        string representation
        """

        return_list = [block.operation.operation_id,
                       self.KEY_VALUE_BLOCK_DIVIDER.join(sorted([key + self.KEY_VALUE_DIVIDER + value
                                                                 for key, value in block.options]))]
        return self.NEST_DIVIDER.join(return_list)

    def input_nest_id(self, block: Block, nest_id: str) -> str:
        """
        Generates unique identifier by block for block's input nest.
        It is supposed to be guaranteed from outside that block contains nest_id.

        :param block:   block to identify
        :param nest_id: nest of the block
        :return:        string representation
        """

        return_list = [block.operation.operation_id,
                       self.KEY_VALUE_BLOCK_DIVIDER.join(sorted([key + self.KEY_VALUE_DIVIDER + value
                                                                 for key, value in block.options])),
                       nest_id + self.INPUT_DIVIDER]
        return self.NEST_DIVIDER.join(return_list)

    def output_nest_id(self, block: Block, nest_id: str) -> str:
        """
        Generates unique identifier by block for block's output nest.
        It is supposed to be guaranteed from outside that block contains nest_id.

        :param block:   block to identify
        :param nest_id: nest of the block
        :return:        string representation
        """

        return_list = [block.operation.operation_id,
                       self.KEY_VALUE_BLOCK_DIVIDER.join(sorted([key + self.KEY_VALUE_DIVIDER + value
                                                                 for key, value in block.options])),
                       nest_id + self.OUTPUT_DIVIDER]
        return self.NEST_DIVIDER.join(return_list)

    def is_input_nest(self, node: GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode) -> bool:
        """
        Checks if given node has identifier of an input nest.

        :param node:    node to specify
        :return:        boolean answer
        """

        return self.INPUT_DIVIDER in str(node.Label)

    def is_output_nest(self, node: GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode) -> bool:
        """
        Checks if given node has identifier of an output nest.

        :param node:    node to specify
        :return:        boolean answer
        """

        return self.OUTPUT_DIVIDER in str(node.Label)

    def is_block(self, node: GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode) -> bool:
        """
        Checks if given node is not neither input nor output nor Root node.

        :param node:    node to specify
        :return:        boolean answer
        """

        return not self.is_input_nest(node) \
               and not self.is_output_nest(node) \
               and not node == GraphWithRepetitiveNodesWithRoot.ROOT

    def get_input_nest(self, node: GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode):
        """
        Transformation from input node back to parameters
        that can specify origin block.

        :param node:    node to transform
        :return:        tuple of operation id, options
        and input nest of the origin block
        """

        splitted = str(node.Label).split(self.NEST_DIVIDER)
        assert len(splitted) == 3
        operation_id, key_values, input_nest = splitted[0], splitted[1], splitted[2]
        key_values = dict([tuple(key_value.split(self.KEY_VALUE_DIVIDER))
                           for key_value in key_values.split(self.KEY_VALUE_BLOCK_DIVIDER)]
                          if len(key_values) > 0 else [])
        return operation_id, key_values, input_nest.split(self.INPUT_DIVIDER)[0]

    def get_output_nest(self, node: GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode):
        """
        Transformation from output node back to parameters
        that can specify origin block.

        :param node:    node to transform
        :return:        tuple of operation id, options
        and output nest of the origin block
        """

        splitted = str(node.Label).split(self.NEST_DIVIDER)
        assert len(splitted) == 3
        operation_id, key_values, output_nest = splitted[0], splitted[1], splitted[2]
        key_values = dict([tuple(key_value.split(self.KEY_VALUE_DIVIDER))
                           for key_value in key_values.split(self.KEY_VALUE_BLOCK_DIVIDER)]
                          if len(key_values) > 0 else [])
        return operation_id, key_values, output_nest.split(self.OUTPUT_DIVIDER)[0]

    def get_block_id(self, node: GraphWithRepetitiveNodesWithRoot.LabeledRepetitiveNode):
        """
        Transformation from block node back to parameters
        that can specify origin block.

        :param node:    node to transform
        :return:        tuple of operation id, options of the origin block
        """

        splitted = str(node.Label).split(self.NEST_DIVIDER)
        assert len(splitted) == 2
        operation_id, key_values = splitted[0], splitted[1]
        key_values = dict([tuple(key_value.split(self.KEY_VALUE_DIVIDER))
                           for key_value in key_values.split(self.KEY_VALUE_BLOCK_DIVIDER)]
                          if len(key_values) > 0 else [])
        return operation_id, key_values

    def convert(self, workflow: Workflow) -> GraphWithRepetitiveNodesWithRoot:
        """
        Converts workflow to simple graph
        by expanding all its blocks in series of nodes
        so that every input/output nest has its node representation.
        Is reversible transformation.

        :param workflow:    workflow to transform
        :return:            graph representation
        """

        graph = rnr_graph()

        from collections import defaultdict
        number_of_blocks = defaultdict(int)

        for block in workflow:
            number_of_blocks[block] += 1
            block_node = lr_node(self.block_id(block),
                                 number_of_blocks[block])
            graph.add_node(block_node)

            for nest in block.operation.inputs:
                nest_node = lr_node(self.input_nest_id(block, nest),
                                    number_of_blocks[block])
                graph.add_node(nest_node)
                graph.add_edge_exp(nest_node,
                                   block_node)

            for nest in block.operation.outputs:
                nest_node = lr_node(self.output_nest_id(block, nest),
                                    number_of_blocks[block])
                graph.add_node(nest_node)
                graph.add_edge_exp(block_node,
                                   nest_node)

        for (from_block, from_num, output_nest), a2 in workflow.items():
            for to_block, to_num, input_nest in a2:
                graph.add_edge_exp(lr_node(self.output_nest_id(from_block,
                                                               output_nest),
                                           from_num),
                                   lr_node(self.input_nest_id(to_block,
                                                              input_nest),
                                           to_num))

        for (from_block, from_num), a2 in workflow.items_by_exc():
            for to_block, to_num in a2:
                graph.add_edge_exp(lr_node(self.block_id(from_block),
                                           from_num),
                                   lr_node(self.block_id(to_block),
                                           to_num))

        return graph

    def reverse_graph(self, graph: GraphWithRepetitiveNodesWithRoot) -> Workflow:
        """
        Reverse transformation from graph to workflow.
        Possibility of such transformation should be guaranteed from outside
        or UB will happen.

        :param graph:   graph to transform
        :return:        original workflow
        """

        workflow = Workflow()

        from collections import defaultdict
        inputs = defaultdict(set)
        outputs = defaultdict(set)
        block_blank = set()

        for node in graph:
            if self.is_input_nest(node):
                operation_id, key_values, nest = self.get_input_nest(node)
                inputs[operation_id, tuple(key_values.items()), node.Number].add(nest)
                block_blank.add((operation_id,
                                 tuple(key_values.items()),
                                 node.Number))

            elif self.is_output_nest(node):
                operation_id, key_values, nest = self.get_output_nest(node)
                outputs[operation_id, tuple(key_values.items()), node.Number].add(nest)
                block_blank.add((operation_id,
                                 tuple(key_values.items()),
                                 node.Number))

            elif node != GraphWithRepetitiveNodesWithRoot.ROOT:
                operation_id, key_values = self.get_block_id(node)
                block_blank.add((operation_id,
                                 tuple(key_values.items()),
                                 node.Number))

        for operation_id, key_values, number in block_blank:
            block_input = inputs[operation_id, tuple(key_values.items()), number]
            block_output = outputs[operation_id, tuple(key_values.items()), number]
            workflow.add_block(new_block=Block(operation=Operation(operation_id=operation_id,
                                                                   inputs=block_input,
                                                                   outputs=block_output),
                                               options=key_values))

        for from_node in graph:
            if self.is_output_nest(from_node):
                from_operation_id, from_key_values, from_nest = self.get_output_nest(from_node)
                for to_node in graph.get_list_of_adjacent_nodes(from_node):
                    if not self.is_input_nest(to_node):
                        continue
                    to_operation_id, to_key_values, to_nest = self.get_input_nest(to_node)
                    from_input = inputs[from_operation_id,
                                        tuple(from_key_values.items()),
                                        from_node.Number]
                    from_output = outputs[from_operation_id,
                                          tuple(from_key_values.items()),
                                          from_node.Number]
                    to_input = inputs[to_operation_id,
                                      tuple(to_key_values.items()),
                                      to_node.Number]
                    to_output = outputs[to_operation_id,
                                        tuple(to_key_values.items()),
                                        to_node.Number]
                    workflow.add_connection_by_data(
                        from_block=Block(operation=Operation(operation_id=from_operation_id,
                                                             inputs=from_input,
                                                             outputs=from_output),
                                         options=from_key_values),
                        from_number=from_node.Number,
                        output_nest=from_nest,
                        to_block=Block(operation=Operation(operation_id=to_operation_id,
                                                           inputs=to_input,
                                                           outputs=to_output),
                                       options=to_key_values),
                        to_number=to_node.Number,
                        input_nest=to_nest
                    )
            elif self.is_input_nest(from_node):
                pass
            elif from_node != GraphWithRepetitiveNodesWithRoot.ROOT:
                from_operation_id, from_key_values = self.get_block_id(from_node)
                for to_node in graph.get_list_of_adjacent_nodes(from_node):
                    if self.is_input_nest(to_node) and self.is_output_nest(to_node):
                        to_operation_id, to_key_values = self.get_block_id(to_node)
                        from_input = inputs[from_operation_id,
                                            tuple(from_key_values.items()),
                                            from_node.Number],
                        from_output = outputs[from_operation_id,
                                              tuple(from_key_values.items()),
                                              from_node.Number]
                        to_input = inputs[to_operation_id,
                                          tuple(to_key_values.items()),
                                          to_node.Number]
                        to_output = outputs[to_operation_id,
                                            tuple(to_key_values.items()),
                                            to_node.Number]
                        workflow.add_connection_by_execution(
                            from_block=Block(operation=Operation(operation_id=from_operation_id,
                                                                 inputs=from_input,
                                                                 outputs=from_output),
                                             options=from_key_values),
                            from_number=from_node.Number,
                            to_block=Block(Operation(operation_id=to_node.Label,
                                                     inputs=to_input,
                                                     outputs=to_output),
                                           options=to_key_values),
                            to_number=to_node.Number)

        return workflow

    def convert_graph_map(self, graph_map: GraphMap) -> (Workflow, GraphDotColorer):
        """
        Converts graph map to workflow and colorer object.

        :param graph_map:   graph map to transform
        :return:            workflow and colorer
        """

        matched_color = self.matched_color
        added_color = self.added_color
        deleted_color = self.deleted_color

        graph_map.eval_difference_complete()

        workflow = Workflow()

        from collections import defaultdict
        inputs = defaultdict(set)
        outputs = defaultdict(set)
        nest_to_center = {}

        for from_node, to_node in graph_map.get_edge_overlap_from_second() \
                                  + graph_map.get_edges_in_2_not_in_1():
            if self.is_input_nest(from_node) and self.is_block(to_node):
                from_operation_id, from_key_values, from_nest = self.get_input_nest(from_node)
                to_operation_id, to_key_values = self.get_block_id(to_node)

                assert to_operation_id == from_operation_id
                assert to_key_values == from_key_values

                inputs[to_node, 2].add(from_nest)
                nest_to_center[from_node, 2] = to_node, 2

            elif self.is_block(from_node) and self.is_output_nest(to_node):
                from_operation_id, from_key_values = self.get_block_id(from_node)
                to_operation_id, to_key_values, to_nest = self.get_output_nest(to_node)

                assert to_operation_id == from_operation_id
                assert to_key_values == from_key_values

                outputs[from_node, 2].add(to_nest)
                nest_to_center[to_node, 2] = from_node, 2

        for from_node, to_node in graph_map.get_edges_in_1_not_in_2() \
                                  + graph_map.get_edge_overlap_from_first():
            if self.is_input_nest(from_node) and self.is_block(to_node):
                from_operation_id, from_key_values, from_nest = self.get_input_nest(from_node)
                to_operation_id, to_key_values = self.get_block_id(to_node)

                assert to_operation_id == from_operation_id
                assert to_key_values == from_key_values

                inputs[to_node, 1].add(from_nest)
                nest_to_center[from_node, 1] = to_node, 1

            elif self.is_block(from_node) and self.is_output_nest(to_node):
                from_operation_id, from_key_values = self.get_block_id(from_node)
                to_operation_id, to_key_values, to_nest = self.get_output_nest(to_node)

                assert to_operation_id == from_operation_id
                assert to_key_values == from_key_values

                outputs[from_node, 1].add(to_nest)
                nest_to_center[to_node, 1] = from_node, 1

        block_colors = {}
        blocks = {}

        for node in graph_map.get_node_overlap_from_second():
            if not self.is_block(node):
                continue
            operation_id, key_values = self.get_block_id(node)
            key_values_tuple = tuple(key_values.items())
            block = Block(Operation(operation_id=operation_id,
                                    inputs=sorted(inputs[node, 2]),
                                    outputs=sorted(outputs[node, 2])),
                          options=key_values_tuple)
            blocks[node, 2] = block, workflow.add_block(block)
            block_colors[blocks[node, 2]] = matched_color

        for node in graph_map.get_nodes_in_2_not_in_1():
            if not self.is_block(node):
                continue
            operation_id, key_values = self.get_block_id(node)
            key_values_tuple = tuple(key_values.items())
            block = Block(Operation(operation_id=operation_id,
                                    inputs=sorted(inputs[node, 2]),
                                    outputs=sorted(outputs[node, 2])),
                          options=key_values_tuple)
            blocks[node, 2] = block, workflow.add_block(block)
            block_colors[blocks[node, 2]] = added_color

        for node in graph_map.get_nodes_in_1_not_in_2():
            if not self.is_block(node):
                continue
            operation_id, key_values = self.get_block_id(node)
            key_values_tuple = tuple(key_values.items())
            block = Block(Operation(operation_id=operation_id,
                                    inputs=sorted(inputs[node, 1]),
                                    outputs=sorted(outputs[node, 1])),
                          options=key_values_tuple)
            blocks[node, 1] = block, workflow.add_block(block)
            block_colors[blocks[node, 1]] = deleted_color

        for node in graph_map.get_node_overlap_from_first():
            if not self.is_block(node):
                continue
            map_node = graph_map.map_from_1(node)
            blocks[node, 1] = blocks[map_node, 2]
            block_colors[blocks[node, 1]] = matched_color

        data_connection_colors = {}
        exc_connection_colors = {}

        for from_node, to_node in graph_map.get_edges_in_2_not_in_1():
            if self.is_output_nest(from_node) and self.is_input_nest(to_node):
                _, _, from_nest = self.get_output_nest(from_node)
                _, _, to_nest = self.get_input_nest(to_node)
                from_nest_block, from_nest_block_number = blocks[nest_to_center[from_node, 2]]
                to_nest_block, to_nest_block_number = blocks[nest_to_center[to_node, 2]]
                workflow.add_connection_by_data(from_block=from_nest_block,
                                                from_number=from_nest_block_number,
                                                output_nest=from_nest,
                                                to_block=to_nest_block,
                                                to_number=to_nest_block_number,
                                                input_nest=to_nest)
                data_connection_colors[from_nest_block,
                                       from_nest_block_number,
                                       from_nest,
                                       to_nest_block,
                                       to_nest_block_number,
                                       to_nest] = added_color
            elif self.is_block(from_node) and self.is_block(to_node):
                from_block, from_number = blocks[from_node, 2]
                to_block, to_number = blocks[to_node, 2]
                workflow.add_connection_by_execution(from_block=from_block,
                                                     from_number=from_number,
                                                     to_block=to_block,
                                                     to_number=to_number)
                exc_connection_colors[from_block,
                                      from_number,
                                      to_block,
                                      to_number] = added_color

        for from_node, to_node in graph_map.get_edge_overlap_from_second() + graph_map.get_edges_in_2_not_in_1():
            if self.is_output_nest(from_node) and self.is_input_nest(to_node):
                _, _, from_nest = self.get_output_nest(from_node)
                _, _, to_nest = self.get_input_nest(to_node)
                from_nest_block, from_nest_block_number = blocks[nest_to_center[from_node, 2]]
                to_nest_block, to_nest_block_number = blocks[nest_to_center[to_node, 2]]
                workflow.add_connection_by_data(from_block=from_nest_block,
                                                from_number=from_nest_block_number,
                                                output_nest=from_nest,
                                                to_block=to_nest_block,
                                                to_number=to_nest_block_number,
                                                input_nest=to_nest)
                data_connection_colors[from_nest_block,
                                       from_nest_block_number,
                                       from_nest,
                                       to_nest_block,
                                       to_nest_block_number,
                                       to_nest] = matched_color \
                    if from_node in graph_map.get_node_overlap_from_second() \
                       and to_node in graph_map.get_node_overlap_from_second() \
                    else added_color
            elif self.is_block(from_node) and self.is_block(to_node):
                from_block, from_number = blocks[from_node, 2]
                to_block, to_number = blocks[to_node, 2]
                workflow.add_connection_by_execution(from_block=from_block,
                                                     from_number=from_number,
                                                     to_block=to_block,
                                                     to_number=to_number)
                exc_connection_colors[from_block,
                                      from_number,
                                      to_block,
                                      to_number] = matched_color \
                    if from_node in graph_map.get_node_overlap_from_second() \
                       and to_node in graph_map.get_node_overlap_from_second() \
                    else added_color

        for from_node, to_node in graph_map.get_edges_in_1_not_in_2():
            if self.is_output_nest(from_node) and self.is_input_nest(to_node):
                _, _, from_nest = self.get_output_nest(from_node)
                _, _, to_nest = self.get_input_nest(to_node)
                from_nest_block, from_nest_block_number = blocks[nest_to_center[from_node, 1]]
                to_nest_block, to_nest_block_number = blocks[nest_to_center[to_node, 1]]
                workflow.add_connection_by_data(from_block=from_nest_block,
                                                from_number=from_nest_block_number,
                                                output_nest=from_nest,
                                                to_block=to_nest_block,
                                                to_number=to_nest_block_number,
                                                input_nest=to_nest)
                data_connection_colors[from_nest_block,
                                       from_nest_block_number,
                                       from_nest,
                                       to_nest_block,
                                       to_nest_block_number,
                                       to_nest] = deleted_color
            elif self.is_block(from_node) and self.is_block(to_node):
                from_block, from_number = blocks[from_node, 1]
                to_block, to_number = blocks[to_node, 1]
                workflow.add_connection_by_execution(from_block=from_block,
                                                     from_number=from_number,
                                                     to_block=to_block,
                                                     to_number=to_number)
                exc_connection_colors[from_block,
                                      from_number,
                                      to_block,
                                      to_number] = deleted_color

        return workflow, GraphMapDotColorer(block_colors, data_connection_colors, exc_connection_colors)
