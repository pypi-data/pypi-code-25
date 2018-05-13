# coding=utf-8
import os

from unittest import TestCase

from .amet import IncompatibleTypeError
from .amet import build_name, dump, load_from_environment, parse_bool
from .amet import FALSY_VALUES, TRUTHY_VALUES


class BuildNameTestCase(TestCase):
    def test_default_params(self):
        key = build_name('key', '', True, '_')
        self.assertEqual(key, 'KEY')

    def test_case_insensitive(self):
        key = build_name('kEy', '', False, '_')
        self.assertEqual(key, 'kEy')

    def test_concatenation(self):
        key = build_name('key', 'prefix', True, '_')
        self.assertEqual(key, 'PREFIX_KEY')

        key = build_name('kEy', 'prEfix', False, '_')
        self.assertEqual(key, 'prEfix_kEy')

        key = build_name('key', 'prefix', True, '+')
        self.assertEqual(key, 'PREFIX+KEY')


class ParseBoolTestCase(TestCase):
    def test_truthy_values(self):
        for tv in TRUTHY_VALUES:
            self.assertTrue(parse_bool(tv))

    def test_falsy_values(self):
        for fv in FALSY_VALUES:
            self.assertFalse(parse_bool(fv))

    def test_unparseable(self):
        with self.assertRaises(ValueError):
            parse_bool('not_bool')


class DumpTestCase(TestCase):
    def test_empty(self):
        dumped = dump({})
        self.assertEqual(dumped, {})

    def test_disallowed_value_type(self):
        invalid = {'key': self}
        with self.assertRaises(IncompatibleTypeError):
            dump(invalid)

    def test_disallowed_key_type(self):
        invalid = {self: 'value'}
        with self.assertRaises(IncompatibleTypeError):
            dump(invalid)

    def test_flat_dictionary(self):
        source = {
            'one': 1,
            'two': 'two',
            'three': True,
            'four': 1.25
        }
        expected = {
            'ONE': '1',
            'TWO': 'two',
            'THREE': 'True',
            'FOUR': '1.25'
        }

        dumped = dump(source)
        self.assertDictEqual(dumped, expected)

    def test_nested_dictionary(self):
        source = {
            'one': 'one',
            'nested': {
                'two': 'two',
                'again': {
                    'three': 'three'
                }
            }
        }
        expected = {
            'ONE': 'one',
            'NESTED_TWO': 'two',
            'NESTED_AGAIN_THREE': 'three'
        }

        dumped = dump(source)
        self.assertDictEqual(dumped, expected)


class LoadTestCase(TestCase):
    def test_empty(self):
        loaded = load_from_environment({})
        self.assertEqual(loaded, {})

    def test_disallowed_value_type(self):
        invalid = {'key': self}
        with self.assertRaises(IncompatibleTypeError):
            load_from_environment(invalid)

    def test_disallowed_key_type(self):
        invalid = {self: 'value'}
        with self.assertRaises(IncompatibleTypeError):
            load_from_environment(invalid)

    def test_type_parsing(self):
        prototype = {
            'A': None,
            'B': 0,
            'C': bool,
            'D': float
        }
        expected = {
            'A': 'a',
            'B': 1,
            'C': False,
            'D': 1.25
        }
        os.environ = {
            'A': 'a',
            'B': '1',
            'C': 'False',
            'D': '1.25'
        }

        loaded = load_from_environment(prototype)
        self.assertDictEqual(loaded, expected)

    def test_missing_variable(self):
        prototype = {
            'A': str
        }
        os.environ = {}

        with self.assertRaises(KeyError):
            load_from_environment(prototype)

    def test_bad_value_type(self):
        prototype = {
            'A': int
        }
        os.environ = {
            'A': 'cant parse this'
        }

        with self.assertRaises(ValueError):
            load_from_environment(prototype)

    def test_nested_dicts(self):
        prototype = {
            'A': None,
            'B': {
                'C': None,
                'D': {
                    'E': None
                }
            }
        }
        os.environ = {
            'A': 'A',
            'B_C': 'BC',
            'B_D_E': 'BDE'
        }
        expected = {
            'A': 'A',
            'B': {
                'C': 'BC',
                'D': {
                    'E': 'BDE'
                }
            }
        }

        loaded = load_from_environment(prototype)
        self.assertDictEqual(loaded, expected)
