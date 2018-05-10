import unittest
from itertools import combinations

import rethinkdb as R
from hypothesis import given, strategies as st

from anji_orm.syntax.indexes import AbstractIndexPolicy, SingleIndexPolicy, GreedyIndexPolicy, GreedlessIndexPolicy, IndexPolicySetting

from .base import BaseTestCase


function_name = st.text(
    st.characters(min_codepoint=97, max_codepoint=122, whitelist_characters=('_', '2')),
    min_size=5
)

index_list_strategy = st.lists(function_name, min_size=3, max_size=10, unique=True)  # pylint: disable=invalid-name


class AbstractIndexPolicyTest(BaseTestCase):

    @given(
        function_name,
        function_name
    )
    def test_simple_index_creation(self, table_name, index_name):
        print(table_name, index_name)
        target_query = R.table(table_name).index_create(index_name)
        result_query = AbstractIndexPolicy.index_creation_query(index_name, table_name)
        self.assertQueryEqual(target_query, result_query)

    @given(
        function_name,
        function_name,
        index_list_strategy
    )
    def test_compound_index_creation(self, table_name, first_index_name, rest_indexes):
        index_name = f"{first_index_name}:{':'.join(rest_indexes)}"
        index_fields = [R.row[index_name]]
        for index in rest_indexes:
            index_fields.append(R.row[index])
        target_query = R.table(table_name).index_create(
            index_name,
            index_fields
        )
        result_query = AbstractIndexPolicy.index_creation_query(index_name, table_name)
        self.assertQueryEqual(target_query, result_query)


class SingleIndexPolicyTest(unittest.TestCase):

    @given(index_list_strategy)
    def test_single_build_index(self, index_list):
        self.assertEqual(
            index_list,
            SingleIndexPolicy({}).build_secondary_index_list(index_list)
        )

    @given(index_list_strategy)
    def test_single_select_index(self, index_list):
        selected_index, unused_indexes = SingleIndexPolicy({}).select_secondary_index(index_list)
        self.assertEqual(selected_index, index_list[0])
        self.assertEqual(unused_indexes, index_list[1:])


class GreedyIndexPolicyTest(unittest.TestCase):

    @given(index_list_strategy)
    def test_greedy_build_index(self, index_list):
        builded_index_list = GreedyIndexPolicy({}).build_secondary_index_list(index_list)
        target_index_list = []
        target_index_list.extend(index_list)
        index_list = sorted(index_list)
        for combination_size in range(2, len(index_list)):
            target_index_list.extend(
                (':'.join(x) for x in combinations(index_list, combination_size))
            )
        target_index_list.append(":".join(index_list))
        self.assertEqual(target_index_list, builded_index_list)

    @given(index_list_strategy)
    def test_greedy_select_index(self, index_list):
        selected_index, unused_indexes = GreedyIndexPolicy({}).select_secondary_index(index_list)
        self.assertEqual(selected_index, ":".join(sorted(index_list)))
        self.assertEqual(unused_indexes, ())


class GreedylessIndexPolicyTest(unittest.TestCase):

    @given(index_list_strategy)
    def test_build_index(self, index_list):
        single_only = (index_list[0], index_list[-1])
        index_policy = GreedlessIndexPolicy({IndexPolicySetting.only_single_index: single_only})
        builded_index_list = index_policy.build_secondary_index_list(index_list)
        target_index_list = []
        target_index_list.extend(index_list)
        filtered_index_list = sorted(x for x in index_list if x not in single_only)
        for combination_size in range(2, len(filtered_index_list)):
            target_index_list.extend(
                (':'.join(x) for x in combinations(filtered_index_list, combination_size))
            )
        target_index_list.append(":".join(filtered_index_list))
        self.assertEqual(target_index_list, builded_index_list)

    @given(index_list_strategy)
    def test_greedy_select_index(self, index_list):
        single_only = (index_list[0], index_list[-1])
        not_single = tuple(x for x in index_list if x not in single_only)
        index_policy = GreedlessIndexPolicy({IndexPolicySetting.only_single_index: single_only})
        selected_index, unused_indexes = index_policy.select_secondary_index(not_single)
        self.assertEqual(selected_index, ":".join(sorted(not_single)))
        self.assertEqual(unused_indexes, ())

    @given(index_list_strategy)
    def test_single_select_index_index(self, index_list):
        single_only = (index_list[0], index_list[-1])
        index_policy = GreedlessIndexPolicy({IndexPolicySetting.only_single_index: single_only})
        selected_index, unused_indexes = index_policy.select_secondary_index(single_only)
        self.assertEqual(selected_index, single_only[0])
        self.assertEqual(unused_indexes, single_only[1:])
