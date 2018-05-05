import pytest
from kd_tree import *


def test_distance():
    result = distance([4, 5, 6, 7, 8, 6], [1, 2, 8, 6, 4, 8])
    assert result == 6.244997998398398


def test_on_non_list_arguments_distance():
    with pytest.raises(TypeError):
        distance("abc", [1, 2, 3])


def test_closest_point():
    result = closest_point([[4, 5, 6, 7, 8, 6], [1, 2, 8, 6, 4, 8],
                            [8, 1, 4, 6, 8, 9]], [1, 2, 7, 8, 9, 1])
    assert result == [4, 5, 6, 7, 8, 6]


def test_on_non_type_arguments_closest_point():
    with pytest.raises(TypeError):
        closest_point([4, 5, 7], [1, 2, 3])


def test_create_csv():
    result = create_csv([["Campo1", "Campo2"], [[0, 1, 2, 3, 4], 0, 1]])
    assert result is None


def test_on_non_type_parameter_create_csv():
    with pytest.raises(TypeError):
        create_csv([[0, 1], "Campo"])


def test_on_non_type_parameter_list_create_csv():
    with pytest.raises(TypeError):
        create_csv([[0, 1], [1, 2]])


def test_on_non_proper_len_parameter_create_csv():
    with pytest.raises(AttributeError):
        create_csv([["Campo1", "Campo2"], [[0, 1, 2, 1], 0, 1]])


def test_insert_node_right():
    root = Node(0, [0, 1])
    result = root.insert_node([2, 0], 1)
    assert result == root.right


def test_insert_node_left():
    root = Node(0, [0, 1])
    result = root.insert_node([-1, 0], 1)
    assert result == root.left


def test_on_non_type_parameter_insert_node():
    root = Node(0, [0, 1])
    with pytest.raises(TypeError):
        root.insert_node(1, "Node")


def test_on_non_type_parameter_node():
    root = Node(0, [0, 1])
    with pytest.raises(TypeError):
        root.insert_node(1, "Node")


def test_insert_leaf():
    root = Node(0, [0, 1])
    result = root.insert_leaf([1, 2], True)
    assert result is None


def test_on_non_type_parameter_insert_leaf():
    root = Node(0, [0, 1])
    with pytest.raises(TypeError):
        root.insert_leaf([1, 2], 4)
