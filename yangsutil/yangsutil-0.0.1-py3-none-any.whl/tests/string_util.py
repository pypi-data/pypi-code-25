import unittest

from yangsutil import StringUtil


class StringUtilTestCase(unittest.TestCase):
    def test_1_empty_string(self):
        self.assertTrue(
            StringUtil.is_empty_string(string=''),
            msg='string is blank'
        )

        self.assertTrue(
            StringUtil.is_empty_string(string=None),
            msg='string is None'
        )

        self.assertFalse(
            StringUtil.is_empty_string(string=' '),
            msg='string is one word blank'
        )

        self.assertFalse(
            StringUtil.is_empty_string(string='123asdf'),
            msg='string is word'
        )

    def test_2_comma_to_list(self):
        self.assertEqual(
            StringUtil.comma_string_to_list(string="a,b,c,d,efg"),
            ["a", "b", "c", "d", "efg"],
            msg="string to list"
        )

    def test_3_list_to_comma(self):
        self.assertEqual(
            StringUtil.list_to_comma_string(list_item=["1", "2", "3", "4", "efg"]),
            "1,2,3,4,efg",
            msg="list to string"
        )

    def test_4_number_expression(self):
        self.assertEqual(
            StringUtil.number_expression(number="1234"),
            "1,234",
            msg="string integer number test"
        )

        self.assertEqual(
            StringUtil.number_expression(number="1234.1234"),
            "1,234.1234",
            msg="string float number test"
        )

        self.assertEqual(
            StringUtil.number_expression(number=1234),
            "1,234",
            msg="integer test"
        )

        self.assertEqual(
            StringUtil.number_expression(number=1231.2345),
            "1,231.2345",
            msg="float test"
        )

    def test_5_blank_to_underscore(self):
        text = "A Item Is Good!!"

        self.assertEqual(
            StringUtil.blank_to_underscore(plain=text),
            "A_Item_Is_Good!!",
            msg="plain text test"
        )

        self.assertEqual(
            StringUtil.blank_to_underscore(plain=text, is_lower=True),
            "a_item_is_good!!",
            msg="plain text and lower test"
        )
