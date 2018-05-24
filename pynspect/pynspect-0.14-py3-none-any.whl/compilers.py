#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Pynspect package (https://pypi.python.org/pypi/pynspect).
# Originally part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/).
# Copyright (C) since 2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module provides tools for compiling filtering rule trees into data structures
more appropriate for actual filtering of `IDEA <https://idea.cesnet.cz/en/index>`__ messages.

There are following main tools in this package:

* :py:class:`IDEAFilterCompiler`

  Filter compiler, that ensures appropriate data types for correct variable
  comparison evaluation in `IDEA <https://idea.cesnet.cz/en/index>`__ messages.

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>"


import re
import datetime


import ipranges
from pynspect.rules import Rule, IPV4Rule, IPV6Rule, DatetimeRule, TimedeltaRule,\
    IntegerRule, FloatRule, NumberRule, VariableRule, LogicalBinOpRule,\
    UnaryOperationRule, ComparisonBinOpRule, MathBinOpRule, ConstantRule,\
    ListRule, FunctionRule
from pynspect.traversers import ListIP, BaseFilteringTreeTraverser


TIMESTAMP_RE = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})[Tt]([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]+))?([Zz]|(?:[+-][0-9]{2}:[0-9]{2}))$")

DURATION_RE = re.compile(r"^((?P<days>[0-9]+)[D|d])?(?P<hrs>[0-9]{2}):(?P<mins>[0-9]{2}):(?P<secs>[0-9]{2})$")


def compile_ip_v4(rule):
    """
    Compiler helper method: attempt to compile constant into object representing
    IPv4 address to enable relations and thus simple comparisons using Python
    operators.
    """
    if isinstance(rule.value, ipranges.Range):
        return rule
    return IPV4Rule(ipranges.from_str_v4(rule.value))

def compile_ip_v6(rule):
    """
    Compiler helper method: attempt to compile constant into object representing
    IPv6 address to enable relations and thus simple comparisons using Python
    operators.
    """
    if isinstance(rule.value, ipranges.Range):
        return rule
    return IPV6Rule(ipranges.from_str_v6(rule.value))

def compile_datetime(rule):
    """
    Compiler helper method: attempt to compile constant into object representing
    datetime object to enable relations and thus simple comparisons using Python
    operators.
    """
    if isinstance(rule.value, datetime.datetime):
        return rule
    try:
        # Try numeric type
        return DatetimeRule(datetime.datetime.fromtimestamp(float(rule.value)))
    except (TypeError, ValueError):
        pass
    # Try RFC3339 timestamp string
    res = TIMESTAMP_RE.match(str(rule.value))
    if res is not None:
        year, month, day, hour, minute, second = (int(n or 0) for n in res.group(*range(1, 7)))
        us_str = (res.group(7) or "0")[:6].ljust(6, "0")
        us_int = int(us_str)
        zonestr = res.group(8)
        zonespl = (0, 0) if zonestr in ['z', 'Z'] else [int(i) for i in zonestr.split(":")]
        zonediff = datetime.timedelta(minutes = zonespl[0]*60+zonespl[1])
        return DatetimeRule(datetime.datetime(year, month, day, hour, minute, second, us_int) - zonediff)
    else:
        raise ValueError("Wrong datetime format '{}'".format(rule.value))

def compile_timedelta(rule):
    """
    Compiler helper method: attempt to compile constant into object representing
    timedelta object to enable math operations and relations with datetime objects
    using Python operators.
    """
    if isinstance(rule.value, datetime.timedelta):
        return rule
    try:
        # Try numeric type
        return TimedeltaRule(datetime.timedelta(seconds = int(rule.value)))
    except:
        pass
    # Try RFC3339 timestamp string
    res = DURATION_RE.match(str(rule.value))
    if res is not None:
        days, hours, minutes, seconds = (int(n or 0) for n in res.group('days','hrs','mins','secs'))
        return TimedeltaRule(datetime.timedelta(days = days, hours = hours, minutes = minutes, seconds = seconds))
    else:
        raise ValueError("Wrong timedelta format '{}'".format(rule.value))

def compile_timeoper(rule):
    """
    Compiler helper method: attempt to compile constant into object representing
    datetime or timedelta object to enable relations and thus simple comparisons
    using Python operators.
    """
    if isinstance(rule.value, (datetime.datetime, datetime.timedelta)):
        return rule
    if isinstance(rule, NumberRule):
        return compile_timedelta(rule)
    if isinstance(rule, ConstantRule):
        try:
            return compile_datetime(rule)
        except ValueError:
            pass
        try:
            return compile_timedelta(rule)
        except ValueError:
            pass
    raise ValueError("Wrong time operation constant '{}'".format(rule))


CVRE = re.compile(r'\[\d+\]')
def clean_variable(var):
    """
    Remove any array indices from variable name to enable indexing into :py:data:`COMPILATIONS_IDEA_OBJECT_CMP`
    callback dictionary.

    This dictionary contains postprocessing callback appropriate for opposing
    operand of comparison operation for variable on given JPath.
    """
    return CVRE.sub('', var)


class IPListRule(ListRule):
    """
    Custom rule for lists of IP addresses/ranges/networks, that need special
    handling in comparison operations.
    """

    def __init__(self, rules):
        """
        Initialize the constant with given value.
        """
        self.value = rules

    def values(self):
        return ListIP([i.value for i in self.value])

    def __repr__(self):
        return "IPLIST({})".format(', '.join([repr(v) for v in self.value]))


class ConversionRule(Rule):
    """
    Custom rule for delayed rule conversions. Can be used by the compiler to
    wrap given rule tree into rule, that can perform arbitrary conversion or
    manipulation with the result of traversal of that rule tree before returning
    the result.
    """
    def __init__(self, conversion, rule):
        self.conversion = conversion
        self.rule = rule

    def __str__(self):
        return '{{{}}}:{}'.format(str(self.rule), self.conversion.__name__)

    def __repr__(self):
        return "CONVERSION({}:{})".format(repr(self.rule), self.conversion.__name__)

    def traverse(self, traverser, **kwargs):
        """
        Implementation of mandatory interface for traversing the whole rule tree.
        This method will call the ``traverse`` method of child rule tree and
        then perform arbitrary conversion of the result before returning it back.
        The optional ``kwargs`` are passed down to traverser callback as additional
        arguments and can be used to provide additional data or context.

        :param pynspect.rules.RuleTreeTraverser traverser: Traverser object providing appropriate interface.
        :param dict kwargs: Additional optional keyword arguments to be passed down to traverser callback.
        """
        result = self.rule.traverse(traverser, **kwargs)
        return self.conversion(result)


class IDEAFilterCompiler(BaseFilteringTreeTraverser):
    """
    Rule tree traverser implementing IDEA filter compilation algorithm.

    Following example demonstrates DataObjectFilter usage in conjuction with
    PynspectFilterParser::

    >>> msg_idea = lite.Idea(test_msg)
    >>> flt = DataObjectFilter()
    >>> cpl = IDEAFilterCompiler()
    >>> psr = PynspectFilterParser()
    >>> psr.build()
    >>> rule = psr.parse('ID like "e214d2d9"')
    >>> rule = cpl.compile(rule)
    >>> result = flt.filter(rule, test_msg)
    """

    def __init__(self):
        super(IDEAFilterCompiler, self).__init__()

        self.compilations_variable = {}
        self.compilations_function = {}

        self.register_variable_compilation('CreateTime',   compile_timeoper, ListRule)
        self.register_variable_compilation('DetectTime',   compile_timeoper, ListRule)
        self.register_variable_compilation('EventTime',    compile_timeoper, ListRule)
        self.register_variable_compilation('CeaseTime',    compile_timeoper, ListRule)
        self.register_variable_compilation('WinStartTime', compile_timeoper, ListRule)
        self.register_variable_compilation('WinEndTime',   compile_timeoper, ListRule)
        self.register_variable_compilation('Source.IP4',   compile_ip_v4,    IPListRule)
        self.register_variable_compilation('Target.IP4',   compile_ip_v4,    IPListRule)
        self.register_variable_compilation('Source.IP6',   compile_ip_v6,    IPListRule)
        self.register_variable_compilation('Target.IP6',   compile_ip_v6,    IPListRule)

        self.register_function_compilation('utcnow', compile_timeoper, ListRule)

    def compile(self, rule):
        """
        Compile given filtering rule into format appropriate for processing IDEA
        messages.

        :param pynspect.rules.Rule rule: filtering rule to be compiled
        :return: compiled filtering rule
        :rtype: pynspect.rules.Rule
        """
        return rule.traverse(self)

    def register_variable_compilation(self, path, compilation_cbk, listclass):
        """
        Register given compilation method for variable on given path.

        :param str path: JPath for given variable.
        :param callable compilation_cbk: Compilation callback to be called.
        :param class listclass: List class to use for lists.
        """
        self.compilations_variable[path] = {
            'callback':  compilation_cbk,
            'listclass': listclass
        }

    def register_function_compilation(self, func, compilation_cbk, listclass):
        """
        Register given compilation method for given function.

        :param str path: Function name.
        :param callable compilation_cbk: Compilation callback to be called.
        :param class listclass: List class to use for lists.
        """
        self.compilations_function[func] = {
            'callback':  compilation_cbk,
            'listclass': listclass
        }

    #---------------------------------------------------------------------------

    @staticmethod
    def _cor_compile(rule, var, val, result_class, key, compilation_list):
        """
        Actual compilation worker method.
        """
        compilation = compilation_list.get(key, None)
        if compilation:
            if isinstance(val, ListRule):
                result = []
                for itemv in val.value:
                    result.append(compilation['callback'](itemv))

                val = compilation['listclass'](result)
            else:
                val = compilation['callback'](val)
        return result_class(rule.operation, var, val)

    def _compile_operation_rule(self, rule, left, right, result_class):
        """
        Compile given operation rule, when possible for given compination of
        operation operands.
        """

        # Make sure variables always have constant with correct datatype on the
        # opposite side of operation.
        if isinstance(left, VariableRule) and isinstance(right, (ConstantRule, ListRule)):
            return self._cor_compile(
                rule,
                left,
                right,
                result_class,
                clean_variable(left.value),
                self.compilations_variable
            )
        if isinstance(right, VariableRule) and isinstance(left, (ConstantRule, ListRule)):
            return self._cor_compile(
                rule,
                right,
                left,
                result_class,
                clean_variable(right.value),
                self.compilations_variable
            )

        # Make sure functions always have constant with correct datatype on the
        # opposite side of operation.
        if isinstance(left, FunctionRule) and isinstance(right, (ConstantRule, ListRule)):
            return self._cor_compile(
                rule,
                left,
                right,
                result_class,
                left.function,
                self.compilations_function
            )
        if isinstance(right, FunctionRule) and isinstance(left, (ConstantRule, ListRule)):
            return self._cor_compile(
                rule,
                right,
                left,
                result_class,
                right.function,
                self.compilations_function
            )

        # In all other cases just keep things the way they are.
        return result_class(rule.operation, left, right)

    def _calculate_operation_math(self, rule, left, right):
        """
        Perform compilation of given math operation by actually calculating given
        math expression.
        """

        # Attempt to keep integer data type for the result, when possible.
        if isinstance(left, IntegerRule) and isinstance(right, IntegerRule):
            result = self.evaluate_binop_math(rule.operation, left.value, right.value)
            if isinstance(result, list):
                return ListRule([IntegerRule(r) for r in result])
            return IntegerRule(result)

        # Otherwise the result is float.
        if isinstance(left, NumberRule) and isinstance(right, NumberRule):
            result = self.evaluate_binop_math(rule.operation, left.value, right.value)
            if isinstance(result, list):
                return ListRule([FloatRule(r) for r in result])
            return FloatRule(result)

        # This point should never be reached.
        raise Exception()


    #---------------------------------------------------------------------------


    def ipv4(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.ipv4` interface.
        """
        rule = compile_ip_v4(rule)
        return rule

    def ipv6(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.ipv6` interface.
        """
        rule = compile_ip_v4(rule)
        return rule

    def datetime(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.datetime` interface.
        """
        rule = compile_datetime(rule)
        return rule

    def timedelta(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.timedelta` interface.
        """
        rule = compile_timedelta(rule)
        return rule

    def integer(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.integer` interface.
        """
        rule.value = int(rule.value)
        return rule

    def float(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.float` interface.
        """
        rule.value = float(rule.value)
        return rule

    def constant(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.constant` interface.
        """
        return rule

    def variable(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.variable` interface.
        """
        return rule

    def list(self, rule, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.list` interface.
        """
        return rule

    def binary_operation_logical(self, rule, left, right, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.binary_operation_logical` interface.
        """
        return LogicalBinOpRule(rule.operation, left, right)

    def binary_operation_comparison(self, rule, left, right, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.binary_operation_comparison` interface.
        """
        return self._compile_operation_rule(
            rule,
            left,
            right,
            ComparisonBinOpRule
        )

    def binary_operation_math(self, rule, left, right, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.binary_operation_math` interface.
        """
        if isinstance(left, NumberRule) and isinstance(right, NumberRule):
            return self._calculate_operation_math(rule, left, right)
        return self._compile_operation_rule(
            rule,
            left,
            right,
            MathBinOpRule
        )

    def unary_operation(self, rule, right, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.unary_operation` interface.
        """
        return UnaryOperationRule(rule.operation, right)

    def function(self, rule, args, **kwargs):
        """
        Implementation of :py:func:`pynspect.traversers.RuleTreeTraverser.function` interface.
        """
        return rule


#-------------------------------------------------------------------------------


#
# Perform the demonstration.
#
if __name__ == "__main__":

    import pprint

    DEMO_DATA     = {"Test": 15, "Attr": "ABC"}
    DEMO_RULE     = ComparisonBinOpRule('OP_GT', VariableRule("Test"), IntegerRule(10))
    DEMO_COMPILER = IDEAFilterCompiler()
    pprint.pprint(DEMO_COMPILER.compile(DEMO_RULE))
