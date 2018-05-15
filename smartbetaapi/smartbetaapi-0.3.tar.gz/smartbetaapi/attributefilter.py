from .enums import AttributeOperator


class AttributeFilter:
    def __init__(self, query_item_key: str, values: [], operator: AttributeOperator = AttributeOperator.IN):
        """The AttributeFilter class allows you define a universe context based on the attribute values for an entity

        To create an AttributeFilter, specify the attribute QueryItem and the values to filter on.

        AttributeFilter('FS_C:Attribute:GIGS.Level.1', 'Financials')
            -->> creates a filter where GIGS sector is Financials

        The filter can have multiple values associated with it. Simply specify an array of values.

        Attribute values can be either IN or NOT_IN the list provided.

        Args:
            query_item_key: QueryItem key for the Attribute to filter on.
            values: List of values for the QueryItem key to filter on.
            operator (optional): AttributeOperator.IN or AttributeOperator.NOT_IN. Default is IN.
        """
        self._values:[]
        self._query_item_key = query_item_key
        if isinstance(values, str):
            self._values = [values]
        else:
            self._values = values
        self._operator = operator
