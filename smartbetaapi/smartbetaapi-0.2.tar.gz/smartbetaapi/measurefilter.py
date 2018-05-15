from .enums import MeasureOperator


class MeasureFilter:
    def __init__(self,
                 query_item_key: str,
                 value: float,
                 operator: MeasureOperator = MeasureOperator.EQ,
                 end_value: float = None):
        """The MeasureFilter class allows you define a universe context based on measure values for an entity

        To create an MeasureFilter, specify the measure QueryItem and the value to filter on.

        MeasureFilter('FS_A:Measure:FE.EPS.FY1', 0.12, MeasureOperator.GT)
            -->> creates a filter where EPS.FY1 > 0.12

        The filter has a number of operators that can be applied to the value:
            EQ, LT, GT, LT_EQ, GT_EQ, BETWEEN, NOT_BETWEEN

        The BETWEEN, NOT_BETWEEN range operators require the end_value to be specified.

        Args:
            query_item_key: QueryItem key for the Measure to filter on.
            value: The value to filter on. (Min value in case of range operators)
            operator (optional): MeasureOperator.  Default is MeasureOperator.EQ.
            end_value (optional): Used when specifying a range operator. BETWEEN, NOT_BETWEEN
        """
        if end_value is None:
            end_value = value

        self._query_item_key = query_item_key
        self._value = value
        self._operator = operator
        self._end_value = end_value
