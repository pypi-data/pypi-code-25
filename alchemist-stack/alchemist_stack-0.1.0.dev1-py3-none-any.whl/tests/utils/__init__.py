from alchemist_stack.utils import dict_diff

from copy import deepcopy
import unittest

__author__ = 'H.D. "Chip" McCullough IV'

class TestUtilityFunctions(unittest.TestCase):
    def setUp(self):
        self.empty_dict = {}
        self.dict = {
            k : 'abcdefghijklmnopqrstuvwxyz'.index(k) for k in 'abcdefghijklmnopqrstuvwxyz'
        }
        self.inverted_dict = {
            k : (26 - 'abcdefghijklmnopqrstuvwxyz'.index(k)) for k in 'abcdefghijklmnopqrstuvwxyz'
        }

    def test_equal_dictionaries(self):
        diff = dict_diff(self.dict, self.dict)
        self.assertEqual(self.empty_dict, diff,
                         msg='The diff dict has {count} keys.'
                            .format(count=len(diff.keys())))

    def test_inequal_dictionaries(self):
        diff = dict_diff(self.dict, self.inverted_dict)
        self.assertNotEqual(self.empty_dict, diff,
                            msg='The difference dictionary, diff, is empty.')

    def test_inequal_dictionaries_is_equal_to_self_less_one(self):
        diff = dict_diff(self.dict, self.inverted_dict)
        inverted_no_mid = deepcopy(self.inverted_dict)
        inverted_no_mid.pop('n')
        self.assertEqual(inverted_no_mid, diff,
                         msg='The two dictionaries contain different values.')

    def tearDown(self):
        del self.empty_dict
        del self.dict
        del self.inverted_dict

if __name__ == '__main__':
    unittest.main()