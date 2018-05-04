from data import DefaultList


class Parse(object):

    def __init__(self, n):
        self.n = n
        self.heads = [None] * (n - 1)
        self.labels = [None] * (n - 1)
        self.lefts = []
        self.rights = []
        for _ in range(n + 1):
            self.lefts.append(DefaultList(0))
            self.rights.append(DefaultList(0))

    def add(self, head, child, label=None):
        self.heads[child] = head
        self.labels[child] = label
        if child < head:
            self.lefts[head].append(child)
        else:
            self.rights[head].append(child)
