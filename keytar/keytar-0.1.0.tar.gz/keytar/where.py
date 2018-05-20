"""Filter clause"""

class FilterClause:
    __key = False
    __value = False
    __operator = False

    def __init__(self, key, value, operator):
        self.__key = key
        self.__value = value
        self.__operator = operator

    def get_key(self):
        return self.__key

    def get_value(self):
        return self.__value

    def get_operator(self):
        return self.__operator
