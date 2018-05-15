import unittest
from tests import TestAPIServices, TestAttributeFilter, TestMeasureFilter, TestMembershipFilter, TestQueryItem, TestUniverse, TestUniverseByStrategyModel, TestUniverseContext, TestUniverseContextModel, TestUniverseQueryItemModel


def run_test():
    """This module runs all the unittest at once"""

    test_suite = unittest.TestSuite()
    # test_suite.addTest(unittest.makeSuite(TestAPIServices))
    test_suite.addTest(unittest.makeSuite(TestAttributeFilter))
    test_suite.addTest(unittest.makeSuite(TestMembershipFilter))
    test_suite.addTest(unittest.makeSuite(TestMeasureFilter))
    test_suite.addTest(unittest.makeSuite(TestQueryItem))
    test_suite.addTest(unittest.makeSuite(TestUniverse))
    test_suite.addTest(unittest.makeSuite(TestUniverseByStrategyModel))
    test_suite.addTest(unittest.makeSuite(TestUniverseContext))
    test_suite.addTest(unittest.makeSuite(TestUniverseContextModel))
    test_suite.addTest(unittest.makeSuite(TestUniverseQueryItemModel))
    unittest.TextTestRunner().run(test_suite)


run_test()