import re

import pytest

import termstree


def normalizer(txt):
    return ' '.join(re.findall('\w+', txt))


@pytest.fixture
def tree():
    src = """
ЧМ 2018
    Москва [url=www.moscow.ru]
        Лужники
            Москва [info="магазин в лужниках"]
    Санкт-Петербург
        Зенит-Арена
    """
    return termstree.build(src, normalizer)


def test_build(tree):
    root = tree.root
    assert None == root.term
    assert 'ЧМ 2018' == root.children[0].term


def test_search(tree):
    text = 'Города ЧМ 2018: Москва, ... Москва принимает... На стадионе Зенит-Арена'
    hits = tree.search_in(text)
    assert 6 == len(hits)

    assert 'Москва' == hits[0].node.term
    assert {'url': 'www.moscow.ru'} == hits[0].node.data
    assert 2 == hits[0].dhits
    assert 2 == hits[0].ihits

    assert 'Москва' == hits[1].node.term
    assert {'info': 'магазин в лужниках'} == hits[1].node.data
    assert 2 == hits[1].dhits
    assert 0 == hits[1].ihits

    assert 'ЧМ 2018' == hits[2].node.term
    assert None == hits[2].node.data
    assert 1 == hits[2].dhits
    assert 5 == hits[2].ihits


def test_pickling_unpickling(tree):
    import pickle
    data = pickle.dumps(tree)
    tree = pickle.loads(data)
    test_search(tree)
