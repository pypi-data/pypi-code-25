from termstree.node import Node


def test_base():
    node = Node('A', {'k': 'v'})
    assert 'A' == node.term
    assert {'k': 'v'} == node.data
    assert not node.children


def test_parent_child():
    root = Node('root')
    item0 = Node('item0')
    item1 = Node('item1')
    root.add_children((item0, item1))

    item10 = Node('item10')
    item1.add_child(item10)

    assert item0 == root[0]
    # print(root.children)
    assert item1 == root.get_child(1)
    assert item1.parent == root
    assert item10 == root[1, 0]
    assert item10 == root.get_child((1, 0))

    assert item10.parent == item1

    assert item1 == root.remove_child(item1)
    assert item10.parent == item1
    assert item1.parent == None