# -*- encoding:utf-8 -*-

import ast
import flake8
import ast
import re
from uuid import UUID

__author__ = 'Zach Reichert'
__email__ = 'zach.reichert@rackspace.com'
__version__ = '0.1.0'


class MarkChecker(object):
    """
    Flake8 plugin to check the presence of test marks.
    """
    name = 'flake8-pytest-mark'
    version = __version__
    pytest_marks = dict.fromkeys(["pytest_mark{}".format(x) for x in range(1, 50)], {})

    @classmethod
    def add_options(cls, parser):
        kwargs = {'action': 'store', 'default': '', 'parse_from_config': True,
                  'comma_separated_list': True}
        for num in range(1, 50):
            parser.add_option(None, "--pytest-mark{}".format(num), **kwargs)

    @classmethod
    def parse_options(cls, options):
        d = {}
        for pytest_mark, dictionary in cls.pytest_marks.iteritems():
            # retrieve the marks from the passed options
            mark_data = getattr(options, pytest_mark)
            if len(mark_data) != 0:
                parsed_params = {}
                for single_line in mark_data:
                    a = [s.strip() for s in single_line.split('=')]
                    # whitelist the acceptable params
                    if a[0] in ['name', 'value_match', 'value_regex']:
                        parsed_params[a[0]] = a[1]
                d[pytest_mark] = parsed_params
        cls.pytest_marks.update(d)
        # delete any empty rules
        cls.pytest_marks = {x:y for x,y in cls.pytest_marks.items() if len(y) > 0}

    def __init__(self, tree, *args, **kwargs):
        self.tree = tree

    def run(self):
        if len(self.pytest_marks) == 0:
            message = "M401 no configuration found for {}, please provide configured marks in a flake8 config".format(self.name)  # noqa: E501
            yield (0, 0, message, type(self))
        rule_funcs = (self.rule_M5XX, self.rule_M6XX)
        for node in ast.walk(self.tree):
            for rule_func in rule_funcs:
                for rule_name, configured_rule in self.pytest_marks.iteritems():
                    for err in rule_func(node, rule_name, configured_rule):
                        yield err

    def rule_M5XX(self, node, rule_name, rule_conf):
        """Read and validate the input file contents.
        A 5XX rule checks for the presence of a configured 'pytest_mark'
        Marks may be numbered up to 50, example: 'pytest_mark49'

        Args:
            node (ast.AST): A node in the ast.
            rule_name (str): The name of the rule.
            rule_conf (dict): The dictionary containing the properties of the rule
        """
        if isinstance(node, ast.FunctionDef):
            marked = False
            line_num = node.lineno
            if re.match(r'^test_', node.name):
                for decorator in node.decorator_list:
                    try:
                        value = decorator.args[0].s
                        mark_key = decorator.func.attr
                        decorator_type = decorator.func.value.value.id
                        if decorator_type == 'pytest' and mark_key == rule_conf['name']:
                            marked = True
                    except (AttributeError, IndexError, KeyError):
                        pass
                if not marked:
                    code = filter(str.isdigit, str(rule_name)).zfill(2)
                    message = 'M5{} test definition not marked with {}'.format(code, rule_conf['name'])
                    yield (line_num, 0, message, type(self))

    def rule_M6XX(self, node, rule_name, rule_conf):
        """Validate a value to a given mark against a provided regex
        A 6XX requires a configured 5XX rule
        A 6XX rule will not warn if a corresponding 5XX rule validates

        Args:
            node (ast.AST): A node in the ast.
            rule_name (str): The name of the rule.
            rule_conf (dict): The dictionary containing the properties of the rule
        """
        if isinstance(node, ast.FunctionDef):
            configured = False
            match = False
            detailed_error = None
            attempt_value_match = False
            line_num = node.lineno
            if re.search(r'^test_', node.name):
                for decorator in node.decorator_list:
                    try:
                        value = decorator.args[0].s
                        mark_key = decorator.func.attr
                        decorator_type = decorator.func.value.value.id
                        if any(k in rule_conf for k in ('value_regex', 'value_match')):
                            attempt_value_match = True

                        # must be marked and configured to match in order to match the content :)
                        if all([decorator_type == 'pytest', mark_key == rule_conf['name'], attempt_value_match]):
                            configured = True

                            if 'value_regex' in rule_conf:
                                if re.match(rule_conf['value_regex'], value):
                                    match = True
                                else:
                                    detailed_error = "Configured regex: '{}'".format(rule_conf['value_regex'])

                            # only use match if regex is not supplied
                            if 'value_match' in rule_conf and 'value_regex' not in rule_conf:
                                if rule_conf['value_match'] == 'uuid':
                                    try:
                                        UUID(value)
                                        match = True
                                    # excepting Exception intentionally here
                                    # If UUID can't parse the value for any reason its not a valid uuid
                                    except Exception as e:
                                        detailed_error = e

                    # this except is intended to catch errors arising from marks that are incompatible with this tool
                    except (AttributeError, IndexError, KeyError):
                        pass
                if configured and not match:
                    code = filter(str.isdigit, str(rule_name)).zfill(2)
                    message = "M6{} the mark value '{}' does not match the configuration specified by {}, {}".format(code, value, rule_name, detailed_error)   # noqa: E501
                    yield (line_num, 0, message, type(self))
