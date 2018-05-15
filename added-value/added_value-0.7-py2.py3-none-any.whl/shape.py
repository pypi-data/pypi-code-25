from collections import Mapping, deque
from itertools import count, chain

from added_value.items_table_directive import NonStringIterable

def flatten(container):
    for i in container:
        if isinstance(i, (list,tuple)):
            for j in flatten(i):
                yield j
        else:
            yield i

depth_marker = object()
ROOT = object()
LEAF = object()

def breadth_first(obj, leaves=False):
    queue = deque()
    queue.append(obj)
    queue.append(None)
    level_keys = []
    current_level_keys = set()
    while len(queue) > 0:
        node = queue.popleft()
        if node is None:
            level_keys.append(current_level_keys)
            current_level_keys = set()
            queue.append(None)
            if queue[0] is None:
                break
            else:
                continue
        if isinstance(node, Mapping):
            current_level_keys.update(node.keys())
            for value in node.values():
                queue.append(value)
        elif isinstance(node, NonStringIterable):
            current_level_keys.update(range(len(node)))
            for value in node:
                queue.append(value)
        else:
            if leaves:
                current_level_keys.add(node)
    return level_keys




a = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    [10, 11, 12],
]

b = [
    [[5, 6], [1, 9], [3, 5]],
    [[7, 2], [4], [5, 6]],
    [[7, 8], [9, 3],],
    [[1, 9], [2, 9], [3, 6]],
]

c = {
    'alpha': 5,
    'bravo': 5,
    'charlie': 6,
    'delta': 5,
    'foxtrot': 6,
    'golf': 4,
}

d = {
    'alpha': "Fox base alpha".split(),
    'bravo': "Rio bravo".split(),
    'charlie': "Charlie says".split(),
    'delta': "Concorde has a delta wing".split(),
    'foxtrot': "The foxtrot was a popular dance".split(),
    'golf': "Golf spoils a walk in the countryside".split(),
}

e = [
    {'set': 3,
     'pour': 4,
     'serve': 5
     },
    {'serve': 19,
     'set': 12,
     'volley': 9
     },
    {'set': 98,
     'pour': 1,
     'cast': 14
     },
    {'cast': 34,
     'line': 18,
     'fish':8
     }
]
