import ahocorasick
from collections import deque, Counter, namedtuple

# Term tree index search result item
Hit = namedtuple('Hit', 'node, dhits, ihits')


class _EmptyIdx:
    """ ahocorasick.Automaton replacement for empty Automaton.

    Empty ahocorasick.Automaton has a problem - throws error on access."""

    def iter(self, _):
        return []


def _build_index(tree_root, normalizer):
    if not tree_root.children:
        return _EmptyIdx()

    idx = ahocorasick.Automaton()

    # tree traversal
    queue = deque()
    queue.append(tree_root)
    while queue:
        node = queue.popleft()
        term = node.term
        if term:
            if normalizer:
                term = normalizer(term)
            term = ' ' + term + ' '
            term_nodes = idx.get(term, [])
            term_nodes.append(node)
            idx.add_word(term, term_nodes)
        for i, child in enumerate(node.children):
            queue.append(child)
    idx.make_automaton()
    return idx


class Index:
    def __init__(self, terms_tree_root, normalizer=None):
        self._normalizer = normalizer
        self._tree = terms_tree_root
        self._idx = _build_index(terms_tree_root, normalizer)

    def get(self, term, default=None):
        """ Get nodes with the given term

        :param str term:
        :param default:
        :return: list of tree nodes with the term
        """
        if self._normalizer:
            term = self._normalizer(term)
        return self._idx.get(' ' + term + ' ', default)

    def __contains__(self, term):
        if self._normalizer:
            term = self._normalizer(term)
        return ' ' + term + ' ' in self._idx

    def _direct_hits(self, text):
        dhits = Counter()
        if self._normalizer:
            text = self._normalizer(text)
        for _, term_nodes in self._idx.iter(' ' + text + ' '):
            for node in term_nodes:
                dhits[node] += 1
        return dhits

    def hits(self, text, indirect_hits=True):
        dhits = self._direct_hits(text)
        ihits = Counter()
        ihits_default = None
        if indirect_hits:
            ihits_default = 0
            for node, hits_n in dhits.items():
                node = node.parent
                while node != self._tree:
                    ihits[node] += hits_n
                    node = node.parent
        hits = []
        for node, hits_n in dhits.most_common():
            hit = Hit(node=node, dhits=hits_n, ihits=ihits.pop(node, ihits_default))
            hits.append(hit)
        for node, hits_n in ihits.most_common():
            hits.append(Hit(node=node, dhits=0, ihits=hits_n))
        return hits
