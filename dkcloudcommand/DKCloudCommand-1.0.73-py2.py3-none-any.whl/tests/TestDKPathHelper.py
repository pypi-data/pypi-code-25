import unittest

from DKCommonUnitTestSettings import DKCommonUnitTestSettings
from DKPathHelper import DKPathHelper


class TestDKPathHelper(DKCommonUnitTestSettings):
    def test_normalize_01_win(self):
        DKPathHelper.FORCE_WINDOWS = True
        tests = [
            ('one\\two', 'one/two'),
            (None, None),
            ('hello', 'hello'),
            ('', ''),
            ('one/two', 'one/two'),
            ('one/two/three', 'one/two/three')
        ]
        for test in tests:
            in_str = test[0]
            expected = test[1]
            out_str = DKPathHelper.normalize(in_str, DKPathHelper.UNIX)
            self.assertEqual(expected, out_str)

    def test_normalize_01_unix(self):
        DKPathHelper.FORCE_WINDOWS = True
        tests = [
            ('one/two', 'one\\two'),
            (None, None),
            ('hello', 'hello'),
            ('', ''),
            ('one\\two', 'one\\two'),
            ('one\\two\\three', 'one\\two\\three')
        ]
        for test in tests:
            in_str = test[0]
            expected = test[1]
            out_str = DKPathHelper.normalize(in_str, DKPathHelper.WIN)
            self.assertEqual(expected, out_str)

    def test_normalize_list(self):
        DKPathHelper.FORCE_WINDOWS = True
        tests = [
            ([], []),
            (None, None),
            (['one/two', 'one/two'], ['one\\two', 'one\\two'])
        ]
        for test in tests:
            in_list = test[0]
            expected = test[1]
            out_list = DKPathHelper.normalize_list(in_list, DKPathHelper.WIN)
            self.assertEqual(expected, out_list)

    def test_normalize_dict_keys(self):
        DKPathHelper.FORCE_WINDOWS = True
        tests = [
            (dict(), dict()),
            (None, None),
            (
                {'key\\one': 'value\\1', 'key\\two': 'value\\2'},
                {'key/one': 'value\\1', 'key/two': 'value\\2'}
            )
        ]
        for test in tests:
            in_dict = test[0]
            expected = test[1]
            out_dict = DKPathHelper.normalize_dict_keys(in_dict, DKPathHelper.UNIX)
            if expected is not None:
                for k,v in expected.iteritems():
                    self.assertTrue(k in out_dict)
                    self.assertEqual(expected[k], out_dict[k])
            else:
                self.assertIsNone(out_dict)

    def test_normalize_dict_keys_ignore(self):
        DKPathHelper.FORCE_WINDOWS = True
        tests = [
            (dict(), dict()),
            (None, None),
            (
                {'key\\one': 'value\\1', 'key\\two': 'value\\2'},
                {'key\\one': 'value\\1', 'key/two': 'value\\2'}
            )
        ]
        ignore = ['key\\one']
        for test in tests:
            in_dict = test[0]
            expected = test[1]
            out_dict = DKPathHelper.normalize_dict_keys(in_dict, DKPathHelper.UNIX, ignore=ignore)
            if expected is not None:
                for k,v in expected.iteritems():
                    self.assertTrue(k in out_dict)
                    self.assertEqual(expected[k], out_dict[k])
            else:
                self.assertIsNone(out_dict)

    def test_normalize_dict_value(self):
        DKPathHelper.FORCE_WINDOWS = True
        tests = [
            (dict(), dict()),
            (None, None),
            (
                {'key1': 'value\\1', 'key2': 'value\\2'},
                {'key1': 'value/1', 'key2': 'value\\2'}
            )
        ]
        for test in tests:
            in_dict = test[0]
            expected = test[1]
            out_dict = DKPathHelper.normalize_dict_value(in_dict, 'key1', DKPathHelper.UNIX)
            if expected is not None:
                for k,v in expected.iteritems():
                    self.assertTrue(k in out_dict)
                    self.assertEqual(expected[k], out_dict[k])
            else:
                self.assertIsNone(out_dict)

    def test_normalize_recipe_dict(self):
        DKPathHelper.FORCE_WINDOWS = True


        recipe_in = {'recipes': {}}
        recipe_in['recipes'] = dict()
        recipe_in['recipes']['recipe1'] = dict()
        recipe_in['recipes']['recipe1']['path/number/1'] = {'sha': 'asdfasdfasdf1'}
        recipe_in['recipes']['recipe1']['path/number/2'] = {'sha': 'asdfasdfasdf2'}
        recipe_in['recipes']['recipe1']['path/number/3'] = {'sha': 'asdfasdfasdf3'}
        recipe_in['recipes']['recipe2'] = dict()
        recipe_in['recipes']['recipe2']['path/number/2_1'] = {'sha': 'asdfasdfasdf2_1'}
        recipe_in['recipes']['recipe2']['path/number/2_2'] = {'sha': 'asdfasdfasdf2_2'}
        recipe_in['recipes']['recipe3'] = dict()
        recipe_in['recipes']['recipe3']['path/number/3'] = {'sha': 'asdfasdfasdf3'}

        recipe_expected = {'recipes': {}}
        recipe_expected['recipes'] = dict()
        recipe_expected['recipes']['recipe1'] = dict()
        recipe_expected['recipes']['recipe1']['path\\number\\1'] = {'sha': 'asdfasdfasdf1'}
        recipe_expected['recipes']['recipe1']['path\\number\\2'] = {'sha': 'asdfasdfasdf2'}
        recipe_expected['recipes']['recipe1']['path\\number\\3'] = {'sha': 'asdfasdfasdf3'}
        recipe_expected['recipes']['recipe2'] = dict()
        recipe_expected['recipes']['recipe2']['path\\number\\2_1'] = {'sha': 'asdfasdfasdf2_1'}
        recipe_expected['recipes']['recipe2']['path\\number\\2_2'] = {'sha': 'asdfasdfasdf2_2'}
        recipe_expected['recipes']['recipe3'] = dict()
        recipe_expected['recipes']['recipe3']['path\\number\\3'] = {'sha': 'asdfasdfasdf3'}


        tests = [
            (dict(), dict()),
            (None, None),
            (
                {'recipes': dict()},
                {'recipes': dict()}
            ),
            (
                recipe_in,
                recipe_expected
            )
        ]
        for test in tests:
            in_dict = test[0]
            expected = test[1]
            out_dict = DKPathHelper.normalize_recipe_dict(in_dict, DKPathHelper.WIN)
            if expected is not None:
                for k,v in expected.iteritems():
                    self.assertTrue(k in out_dict)
                    self.assertEqual(expected[k], out_dict[k])
            else:
                self.assertIsNone(out_dict)

if __name__ == '__main__':
    unittest.main()
