from Class import Class
from Function import Function


class Test:

    def __init__(self):
        pass

    def generate_test_interface(self, cls):
        if len(cls.functions) == 0 or cls.is_test:
            return None
        test = Class()
        test.type = 'class'
        test.name = 'ITest' + cls.name
        test.group = 'tests'
        test.behaviors.append('TestCase')
        for func in cls.functions:
            ignored = ['visit']
            if func.name not in ignored:
                self.add_function(test, 'test_' + func.name)
        if len(test.functions) == 0:
            return None
        return test

    def add_function(self, cls, name):
        function = Function()
        function.name = name
        function.return_type = 'bool'
        function.is_abstract = True
        cls.functions.append(function)
