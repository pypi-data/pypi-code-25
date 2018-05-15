import unittest
from smartbeta_api.measurefilter import MeasureFilter
from smartbeta_api.enums import MeasureOperator


class TestMeasureFilter(unittest.TestCase):

    def test_MeasureFilter(self):
        test_filter = MeasureFilter(measure_name="name", value=0.5, operator=MeasureOperator.EQ, end_value=1.5)
        self.assertEqual(test_filter._measure_name, "name")
        self.assertEqual(test_filter._value, 0.5)
        self.assertEqual(test_filter._operator, MeasureOperator.EQ)
        self.assertEqual(test_filter._end_value, 1.5)


if __name__ == '__main__':
    unittest.main()
