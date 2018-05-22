
import unittest
from design_explorer import graph


class testEdgeMethods(unittest.TestCase):

    def test_node_class_attributes_exist(self):
        oNode = graph.node()
        self.assertEqual(oNode.name, None)
        self.assertEqual(oNode.subNode, None)

    def test_node_class_parameters(self):
        oNode = graph.node('name', 'subNode')
        self.assertEqual(oNode.name, 'name')
        self.assertEqual(oNode.subNode, 'subNode')

    def test_edge_class_attributes_exist(self):
        oEdge = graph.edge()
        self.assertEqual(oEdge.source, None)
        self.assertEqual(oEdge.target, None)
        self.assertEqual(oEdge.name, None)

    def test_edge_class_parameters(self):
        oEdge = graph.edge('source', 'target', 'name')
        self.assertEqual(oEdge.source, 'source')
        self.assertEqual(oEdge.target, 'target')
        self.assertEqual(oEdge.name, 'name')

    def test_trace_class_exists(self):
        oTrace = graph.trace('T1')
        self.assertEqual(oTrace.path, None)
        self.assertEqual(oTrace.name, 'T1')

    def test_trace_add_edge(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        self.assertEqual(oTrace.path[0].source, 'S1')
        self.assertEqual(oTrace.path[1].source, 'S2')
        self.assertEqual(oTrace.path[2].source, 'S3')

    def test_trace_expand_path_with_only_edges(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        lEdges = oTrace.get_expanded_path()
        self.assertEqual(lEdges[0].source, 'S1')
        self.assertEqual(lEdges[1].source, 'S2')
        self.assertEqual(lEdges[2].source, 'S3')

    def test_trace_expand_path_with_only_traces(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        oTrace1 = graph.trace('T2')
        oTrace1.add_to_path(oTrace)
        lEdges = oTrace1.get_expanded_path()
        self.assertEqual(lEdges[0].source, 'S1')
        self.assertEqual(lEdges[1].source, 'S2')
        self.assertEqual(lEdges[2].source, 'S3')

    def test_trace_expand_path_with_only_traces_and_edges(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        oTrace1 = graph.trace('T2')
        oTrace1.add_to_path(oTrace)
        oTrace1.add_to_path(graph.edge('S4', 'T4', 'N4'))
        oTrace1.add_to_path(graph.edge('S5', 'T5', 'N5'))
        lEdges = oTrace1.get_expanded_path()
        self.assertEqual(lEdges[0].source, 'S1')
        self.assertEqual(lEdges[1].source, 'S2')
        self.assertEqual(lEdges[2].source, 'S3')
        self.assertEqual(lEdges[3].source, 'S4')
        self.assertEqual(lEdges[4].source, 'S5')

    def test_trace_expand_path_with_nested_traces(self):
        oTrace = graph.trace('T1')
        oTrace.add_to_path(graph.edge('S1', 'T1', 'N1'))
        oTrace.add_to_path(graph.edge('S2', 'T2', 'N2'))
        oTrace.add_to_path(graph.edge('S3', 'T3', 'N3'))
        oTrace1 = graph.trace('T2')
        oTrace1.add_to_path(oTrace)
        oTrace1.add_to_path(graph.edge('S4', 'T4', 'N4'))
        oTrace1.add_to_path(graph.edge('S5', 'T5', 'N5'))
        oTrace2 = graph.trace('T3')
        oTrace2.add_to_path(graph.edge('S6', 'T6', 'N6'))
        oTrace2.add_to_path(oTrace1)
        lEdges = oTrace2.get_expanded_path()
        self.assertEqual(lEdges[0].source, 'S6')
        self.assertEqual(lEdges[1].source, 'S1')
        self.assertEqual(lEdges[2].source, 'S2')
        self.assertEqual(lEdges[3].source, 'S3')
        self.assertEqual(lEdges[4].source, 'S4')
        self.assertEqual(lEdges[5].source, 'S5')

    def test_base_list_class_attributes_exist(self):
        oNodeList = graph.base_list()
        self.assertEqual(oNodeList.lItems, None)

    def test_base_list_method_add_item(self):
        oNodeList = graph.base_list()
        oNodeList.add_item(graph.node('N1'))
        oNodeList.add_item(graph.node('N2'))
        oNodeList.add_item(graph.node('N3'))
        self.assertEqual(oNodeList.lItems[0].name, 'N1')
        self.assertEqual(oNodeList.lItems[1].name, 'N2')
        self.assertEqual(oNodeList.lItems[2].name, 'N3')

    def test_base_list_method_get_item(self):
        oNodeList = graph.base_list()
        oNodeList.add_item(graph.node('N1'))
        oNodeList.add_item(graph.node('N2'))
        oNodeList.add_item(graph.node('N3'))
        self.assertEqual(oNodeList.get_item('N1').name, 'N1')
        self.assertEqual(oNodeList.get_item('N2').name, 'N2')
        self.assertEqual(oNodeList.get_item('N3').name, 'N3')
        self.assertEqual(oNodeList.get_item('N564'), None)


if __name__ == '__main__':
    unittest.main()
