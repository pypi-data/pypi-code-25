from .fixtures import *

def test_alias(class_with_alias):
    assert class_with_alias.delegated() == 'abc'
