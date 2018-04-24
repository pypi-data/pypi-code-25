from graph_diff.graph_diff_algorithm import GraphDiffAlgorithm
from graph_diff.nirvana_object_model.workflow import Workflow
from graph_diff.nirvana_object_model.workflow_to_dot_converter import WorkflowToDotConverter, print_together
from graph_diff.nirvana_object_model.workflow_to_graph_converter import WorkflowToGraphConverter


class Pipeline:
    """Pipeline for comparison of nirvana workflows"""

    def __init__(self,
                 algorithm: GraphDiffAlgorithm,
                 workflow_converter: WorkflowToGraphConverter):
        """
        :param algorithm:           algorithm to be used
        :param workflow_converter:  workflow converter to simple graph to be used
        """

        self._algo = algorithm
        self._to_abstract_converter = workflow_converter
        self._to_dot_converter = WorkflowToDotConverter

    def get_diff(self,
                 workflow1: Workflow,
                 workflow2: Workflow):
        """
        Evaluates difference between workflow1 and workflow 2.

        :param workflow1:   original workflow
        :param workflow2:   changed workflow
        :return:            tuple of composed workflow and colorer object
        """

        # Transforming given workflow to abstract graphs
        graph1 = self._to_abstract_converter.convert(workflow=workflow1)
        graph2 = self._to_abstract_converter.convert(workflow=workflow2)

        print('len 1', sum([len(graph1.get_list_of_adjacent_nodes(node)) for node in graph1]))
        print('len 2', sum([len(graph2.get_list_of_adjacent_nodes(node)) for node in graph2]))

        # Constructing difference 'twixt abstract graphs.
        graph_map = self._algo.construct_diff(graph1=graph1, graph2=graph2)

        # Evaluation of complete difference between graphs.
        graph_map.eval_difference_complete()

        # print('Score', GraphMapComparatorByEdgeNum().comparable_representation(graph_map))
        # print(graph_map.get_edge_overlap_from_first())
        # print(graph_map.get_edges_in_1_not_in_2())
        # print(graph_map.get_edges_in_2_not_in_1())
        print(len(graph_map.get_edge_overlap_from_first()))
        print(len(graph_map.get_edges_in_1_not_in_2()))
        print(len(graph_map.get_edges_in_2_not_in_1()))

        # Converting graph difference back to normal workflow with function of colors
        return self._to_abstract_converter.convert_graph_map(graph_map=graph_map)

    def get_dot_diff(self,
                     workflow1: Workflow,
                     workflow2: Workflow):
        """
        Evaluated difference between workflows and
        returns a pydot.Dot representation of that.

        :param workflow1:   original workflow
        :param workflow2:   changed workflow
        :return:            pydot.Dot representation of difference
        """
        workflow_diff, block_colors = self.get_diff(workflow1, workflow2)

        # Conversion of workflow with colors to dot.
        dot_diff = self._to_dot_converter().convert_workflow(workflow=workflow_diff,
                                                             colors=block_colors)

        return dot_diff

    def print_diff(self,
                   workflow1: Workflow,
                   workflow2: Workflow,
                   path: str):
        """
        Evaluates difference between worflows and prints
        these difference by specified path.

        :param workflow1:
        :param workflow2:
        :param path:
        :return:
        """
        dot_workflow1 = self._to_dot_converter("1").convert_workflow(workflow=workflow1)
        dot_workflow2 = self._to_dot_converter("2").convert_workflow(workflow=workflow2)

        dot_diff = self.get_dot_diff(workflow1, workflow2)

        print_together(dot_workflow1,
                       dot_diff,
                       dot_workflow2,
                       names=['from_workflow', 'diff_workflow', 'to_workflow']).write(path, format='png')
