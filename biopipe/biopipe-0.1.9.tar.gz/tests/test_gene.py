import biopipe.gene as gene

from nose.tools import assert_equal


def test_get_first_item_given_one_item():
    assert_equal(gene.get_first_item(1), 1)
