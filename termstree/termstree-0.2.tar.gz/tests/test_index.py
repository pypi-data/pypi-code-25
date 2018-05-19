import termstree
from termstree.index import Index, Hit
from termstree.parser import loads
import re

TEST_SRC = """
A[k=v]
    B [k1=v1 "k 2"="v 2"]
    C
        D
E
"""


def test_index_build():
    root = loads(TEST_SRC)
    terms_idx = Index(root)
    assert 'A' in terms_idx
    assert 'B' in terms_idx
    assert 'C' in terms_idx
    assert 'D' in terms_idx
    assert 'E' in terms_idx
    assert 'X' not in terms_idx

    nodes = terms_idx.get('D')
    assert 1 == len(nodes)
    assert 'D' == nodes[0].term

    assert None == terms_idx.get('X')


def test_index_normalization():
    src = """Europe\n\tGermany\n\tMunich\n\tBerlin"""
    text = 'munich BERLIN'
    root = loads(src)
    normalizer = lambda txt: txt.lower()
    terms_idx = Index(root, normalizer=normalizer)
    hits = terms_idx.hits(text, indirect_hits=False)
    assert 2 == len(hits)
    assert 'Munich' == hits[0].node.term
    assert 'Berlin' == hits[1].node.term


def test_index_hits():
    src = """
Europe
    Russia [url=www.russia.ru]
        Moscow
            Europe [info="a place in Moscow"]
    England
        London
"""
    text = 'Europe: London, EUROPE CENTER in Moscow'
    root = loads(src)
    normalizer = lambda txt: ' '.join(re.compile('\w+').findall(txt.lower()))
    terms_idx = Index(root, normalizer=normalizer)

    hits = terms_idx.hits(text, indirect_hits=False)
    assert 4 == len(hits)
    assert [
               Hit(root[0], dhits=2, ihits=None),
               Hit(root[0, 0, 0, 0], dhits=2, ihits=None),
               Hit(root[0, 1, 0], dhits=1, ihits=None),
               Hit(root[0, 0, 0], dhits=1, ihits=None)
           ] == hits

    hits = terms_idx.hits(text)
    assert 6 == len(hits)
    assert [
               Hit(root[0], dhits=2, ihits=4),
               Hit(root[0, 0, 0, 0], dhits=2, ihits=0),
               Hit(root[0, 1, 0], dhits=1, ihits=0),
               Hit(root[0, 0, 0], dhits=1, ihits=2),
               Hit(root[0, 0], dhits=0, ihits=3),
               Hit(root[0, 1], dhits=0, ihits=1),
           ] == hits
