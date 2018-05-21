import unittest

from yangsutil import DictUtil


class DictUtilTestCase(unittest.TestCase):
    def test_1_dict_list_to_dict(self):
        sample_list = [
            {'a': 'b', 'b': 1, 'c': 5.1, 'd': ['a']},
            {'a': 'd', 'b': 5, 'c': 5.2, 'd': ['a', 'bb']},
            {'a': 'e', 'b': 2, 'c': 1.3, 'd': ['q', 123]},
            {'a': 'a', 'b': 0, 'c': 2.44, 'd': ['a', 'dddd']},
            {'a': 'z', 'b': -1, 'c': 5.77, 'd': ['qwer', '!@#!@x']},
            {'a': 't', 'b': -5, 'c': 4.4545, 'd': ['a', '3r2r2']},
        ]

        self.assertDictEqual(
            DictUtil.dict_list_to_dict(sample_list),
            {
                'a': 'bdeazt',
                'b': 2,
                'c': 24.2645,
                'd': ['a', 'a', 'bb', 'q', 123, 'a', 'dddd', 'qwer', '!@#!@x', 'a', '3r2r2']
            },
            msg='normal list'
        )

        sample_list = [
            {'a': [{'name': 'ab', 'item': 'ab'}], 'b': [{'name': 'bc', 'item': 'bw'}]},
            {'a': [{'name': 'wf', 'item': 'wf'}], 'b': [{'name': 'bs', 'item': 'bq'}]},
            {'a': [{'name': 'qq', 'item': 'qq'}], 'b': [{'name': 'bq', 'item': 'bs'}]},
            {'a': [{'name': 'ff', 'item': 'ff'}], 'b': [{'name': 'bw', 'item': 'ba'}]},
        ]

        self.assertDictEqual(
            DictUtil.dict_list_to_dict(sample_list),
            {
                'a': [
                    {'name': 'ab', 'item': 'ab'},
                    {'name': 'wf', 'item': 'wf'},
                    {'name': 'qq', 'item': 'qq'},
                    {'name': 'ff', 'item': 'ff'},
                ],
                'b': [
                    {'name': 'bc', 'item': 'bw'},
                    {'name': 'bs', 'item': 'bq'},
                    {'name': 'bq', 'item': 'bs'},
                    {'name': 'bw', 'item': 'ba'},
                ]
            },
            msg='array list'
        )

        self.assertDictEqual(
            DictUtil.dict_list_to_dict(sample_list, order_key='name'),
            {
                'a': [
                    {'name': 'ab', 'item': 'ab'},
                    {'name': 'ff', 'item': 'ff'},
                    {'name': 'qq', 'item': 'qq'},
                    {'name': 'wf', 'item': 'wf'},
                ],
                'b': [
                    {'name': 'bc', 'item': 'bw'},
                    {'name': 'bq', 'item': 'bs'},
                    {'name': 'bs', 'item': 'bq'},
                    {'name': 'bw', 'item': 'ba'},
                ]
            },
            msg='array list sort'
        )
