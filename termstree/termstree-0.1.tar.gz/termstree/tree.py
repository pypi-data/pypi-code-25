from .index import Index
from .parser import load, loads


class Tree:
    @classmethod
    def build(cls, source, terms_normalizer=None):
        """ Build term tree from source file.

        Normalizers examples:

            lowercase normalizer:
                lambda txt: txt.lower()

            words extraction normalizer:
                lambda txt: ' '.join(re.findall('\w+', txt))

        :param source: str or file object with terms tree source
        :param terms_normalizer: callable object that converts text
        :return: Tree instance
        """
        if isinstance(source, str):
            root = loads(source)
        else:
            root = load(source)
        idx = Index(root, terms_normalizer)
        return cls(root, idx)

    def __init__(self, root_node, index):
        self.root = root_node
        self._index = index

    def search_in(self, text, indirect_hits=True):
        return self._index.hits(text, indirect_hits)
