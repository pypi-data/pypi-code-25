# -*- coding: utf-8 -*-
#
# 2018 Alexander Maslyaev <maslyaev@gmail.com>
#
# No copyright. No license. It's up to you what to do with this text.
# http://creativecommons.org/publicdomain/zero/1.0/

""" This is a compact, portable (no dependencies) and extremely easy-to-use
implementation of self-balancing binary search tree. This particular type of
trees (so called AA-tree) is described here:
https://en.wikipedia.org/wiki/AA_tree

Features:
1. You can use this module through 'import' instruction or simply
   copy-paste the implementation into your source code, and be happy.
2. While instantiating 'sbst' object you can specify your own comparison
   function or use default simple comparison (see '_sbst_simple_comparison'
   implementation below).
3. You can add values to tree one-by-one using function 'add', or fill it from
   some iterable object (function 'addfrom'). Either initialization in
   constructor is possible.
4. The tree stores all duplicates. This feature is vital if the tree is an
   index for in-memory table.
5. This SBST gives you two basic search operations:
   - 'min' - returns minimal value that is not less (if 'inclusive'
     parameter is True) or greater (inclusive=False) than specified limit.
   - 'max' - returns maximal value that is not greater (if 'inclusive'
     parameter is True) or less (inclusive=False) than specified limit.
   If you have not specified limit, functions return respectively minimal or
   maximal value in the tree.
6. Function 'forward_from' returns generator that yields sorted sequence of
   values starting from a specified value. Function 'backward_from' yields
   reverse-sorted sequence down from a specified value. These functions have
   'inclusive' option too. If starting value is not specified, these
   functions yield respectively sorted or reverse-sorted sequences of all
   values in the tree. If tree modified while iterating (some values
   inserted, some removed, tree rebalanced), sequence will be yielded in
   right predictable way.
7. If comparison function treats values as equal, they will be yielded by
   'forward_from' and 'backward_from' generators in the insertion order.
8. Do not store None values into tree. Even if your comparison function can
   process them, you will not be able to search them because None value will
   be treated as 'not specified'.
9. If mutable objects inserted into the tree are changed, their sequence in
   tree may become irrelevant. So after value mutation it is a good idea to
   remove it from tree and add again.
10. Methods 'add' and 'remove' are not thread-safe. Be careful.

Little tutorial (and also doctest):
>>> import aa_sbst
>>> t1 = aa_sbst.sbst() # empty tree with a simple comparison 'by default'
>>> t1.add(123) # iserting values
>>> t1.add(45)  #     one-by-one
>>> t1.max(100) # looking for maximal value not greater than 100
45
>>> t1.min(100) # looking for minimal value not less than 100
123
>>> t1.add(67) # one more value
>>> t1.max(67) # will be 67 because inclusive=True by default
67
>>> t1.max(67, False) # not inclusive
45
>>> t1.max(45, False) # will be None
>>> print(*[v for v in t1.forward_from(50)]) # let's iterate forward...
67 123
>>> print(*[v for v in t1.backward_from(100)]) # ... and backward from 100
67 45
>>> # Now we will modify tree while iterating:
>>> for v in t1.forward_from():
...     t1.add(-v)
>>> print(*[v for v in t1.forward_from()]) # let's see the result
-123 -67 -45 45 67 123
>>> # Using 'stop' parameter of iterating functions
>>> print(*[v for v in t1.forward_from(-100, stop=0)])
-67 -45

>>> # Using custom comparison
>>> def my_cmp(v1, v2): # value[0] ascending then value[1] descending
...     if v1[0] == v2[0] and v1[1] == v2[1]:
...         return 0
...     elif v1[0] < v2[0] or v1[0] == v2[0] and v1[1] > v2[1]:
...         return -1
...     else:
...         return 1
>>> t2 = aa_sbst.sbst(my_cmp) # next time I'll use lambda
>>> t2.add((1, 'a', '1-st'))
>>> t2.add((10, 'p', '2-nd'))
>>> t2.add((5, 'c', '3-rd'))
>>> t2.add((5, 'd', '4-th'))
>>> t2.add((5, 'q', '5-th'))
>>> t2.add((5, 'd', '6-th')) # duplicate by key values with 4-th
>>> [v for v in t2.forward_from((5, 'd'))]
[(5, 'd', '4-th'), (5, 'd', '6-th'), (5, 'c', '3-rd'), (10, 'p', '2-nd')]
>>> [v for v in t2.backward_from((5, 'd'))]
[(5, 'd', '4-th'), (5, 'd', '6-th'), (5, 'q', '5-th'), (1, 'a', '1-st')]
>>> # consider '4-th'..'6-th' order
>>> len(t2) # 'len' operation is also provided
6
>>> t2.remove((10, 'p', '2-nd'))
>>> t2.remove((1, 'a', '1-st'))
>>> [v for v in t2.forward_from()]
[(5, 'q', '5-th'), (5, 'd', '4-th'), (5, 'd', '6-th'), (5, 'c', '3-rd')]
>>> t2.remove((5, 'q', 'never been inserted'))
>>> [v for v in t2.forward_from()]
[(5, 'q', '5-th'), (5, 'd', '4-th'), (5, 'd', '6-th'), (5, 'c', '3-rd')]
>>> # Nothing removed. (5, 'q', '5-th') != (5, 'q', 'never been inserted')
>>> # Value was found by key but it is not a same value
>>> #
>>> t2.add((10, 'p', '7-th')) # some
>>> t2.add((10, 'q', '8-th')) #    extra
>>> t2.add((11, 'r', '9-th')) #       values
>>> # How to get tree-like representation:
>>> for n in t2.nodes_list():
...     lvl = 0
...     c = n
...     while c:
...         c = c.parent
...         lvl += 1
...     print('--'*(lvl-1), str(n.getval()))
-- (5, 'q', '5-th')
---- (5, 'd', '4-th')
 (5, 'c', '3-rd')
---- (10, 'q', '8-th')
-- (10, 'p', '7-th')
---- (11, 'r', '9-th')

>>> # Let's do stress-test
>>> t3 = aa_sbst.sbst(source=range(100000))
>>> sum(t3.forward_from())
4999950000
>>> # ...that is right
>>> t3.root.level
16
>>> # ...seems reasonable

>>> # Some unittest on 'remove'
>>> import random
>>> import collections
>>> import functools
>>> cnt = collections.Counter()
>>> t4 = aa_sbst.sbst()
>>> for _ in range(10000):
...     v = random.randint(-5000, 5000)
...     cnt.update([v])
...     t4.add(v)
>>> for _ in range(30000):
...     v = random.randint(-5000, 5000)
...     if cnt[v] > 0:
...         cnt.subtract([v])
...         t4.remove(v)
>>> etalon = sorted(functools.reduce(lambda a, v: a + [v]*cnt[v], \
    (v for v in cnt.keys() if v >= 0), []))
>>> etalon == [v for v in t4.forward_from(0)]
True

>>> # Test for changing stored value
>>> t5 = aa_sbst.sbst()
>>> t5.add([1])
>>> mutable = [2] # value to change
>>> t5.add(mutable)
>>> t5.add([3])
>>> mutable[0] = 100 # mutated
>>> [v for v in t5.forward_from()] # let`s see bad sequence
[[1], [100], [3]]
>>> t5.remove(mutable) # remove and then add
>>> t5.add(mutable)    # to restore sequence
>>> [v for v in t5.forward_from()]
[[1], [3], [100]]

>>> # 3 tests for renoving values while iterating
>>> # 1: removing current value
>>> t6 = aa_sbst.sbst(source=[1, 2, 3, 99, 100, 101])
>>> for v in t6.forward_from(2):
...     print(v, end=' ')
...     t6.remove(v)
2 3 99 100 101 
>>> # 2: removing next value
>>> t6 = aa_sbst.sbst(source=[1, 2, 3, 99, 100, 101])
>>> for v in t6.forward_from(2):
...     print(v, end=' ')
...     t6.remove(t6.min(v, False))
2 99 101 
>>> # 3: removing previous value
>>> t6 = aa_sbst.sbst(source=[1, 2, 3, 99, 100, 101])
>>> for v in t6.forward_from(2):
...     print(v, end=' ')
...     t6.remove(t6.max(v, False))
2 3 99 100 101 
>>> [v for v in t6.forward_from()]
[101]

>>> # Using make_cmp_fn_by_key
>>> import collections
>>> t_empl = collections.namedtuple('employee', 'id, name, salary')
>>> # Tree will be ordered by salary and then by name:
>>> t7 = aa_sbst.sbst(make_cmp_fn_by_key(lambda v: (v.salary, v.name)))
>>> t7.add(t_empl(1, 'John', 1000))
>>> t7.add(t_empl(2, 'Alice', 1000))
>>> t7.add(t_empl(3, 'Paul', 900))
>>> t7.add(t_empl(4, 'Bob', 1100))
>>> t7.add(t_empl(5, 'Celine', 1050))
>>> print(*[v for v in t7.forward_from()], sep=chr(10))
employee(id=3, name='Paul', salary=900)
employee(id=2, name='Alice', salary=1000)
employee(id=1, name='John', salary=1000)
employee(id=5, name='Celine', salary=1050)
employee(id=4, name='Bob', salary=1100)
>>> print(*[v for v in t7.backward_from(t_empl(0, '-', 1000))], sep=chr(10))
employee(id=3, name='Paul', salary=900)
>>> print(*[v for v in t7.backward_from(t_empl(0, 'ZZZ', 1000))], sep=chr(10))
employee(id=1, name='John', salary=1000)
employee(id=2, name='Alice', salary=1000)
employee(id=3, name='Paul', salary=900)
"""

# -------------- Start copy-paste from here --------------

def _sbst_simple_comparison(v1, v2):
    """ Sorting function by default """
    if v1 == v2:
        return 0
    else:
        return -1 if v1 < v2 else 1

def make_cmp_fn_by_key(key):
    """ Takes a key extraction function and makes comparison function """
    return lambda v1, v2: _sbst_simple_comparison(key(v1), key(v2))

class _sbst_node():
    """ Represents tree node """
    
    def __init__(self, val, parent, direction=None):
        self.level = self.len = 1
        self.left = self.right = None
        self.val = val
        self.is_array = False
        self.parent = parent
        self.direction = direction
    
    def getval(self):
        return self.val if not self.is_array else self.val[0]
    
    def addval(self, val):
        if self.is_array:
            self.val.append(val)
        else:
            self.val = [self.val, val]
            self.is_array = True
        self.len += 1
    
    def dropval(self, val, allcopies):
        """ You need this method only if your sbst has 'remove' method """
        if self.is_array:
            i = 0
            while i < self.len:
                if val == self.val[i]:
                    self.len -= 1
                    self.val = self.val[0 : i] + self.val[i+1 : ]
                    if not allcopies:
                        break
        else:
            if val == self.val:
                self.len = 0

class sbst():
    """ Self-balancing binary search tree, AA-tree form.
    https://en.wikipedia.org/wiki/AA_tree """
    
    def __init__(self, comparison_func=_sbst_simple_comparison, source=None):
        """ Constructor. Parameters:
        comparison_func - function (or lambda) that receives 2 parameters
          and returns -1 if first 'less' then second, 1 if 'greater' and
          0 if parameters considered as 'equal'. If not specified, default
          comparison used (in such case stored objects must implement '<'
          and '==' operations).
        source - iterable object. Convenient for immediate initialization."""
        self.root = None
        self.comp_f = comparison_func
        self._len = 0
        if source != None:
            self.addfrom(source)
    
    def __len__(self):
        return self._len
    
    def add(self, val):
        """ Inserts value into the tree. """
        self.root = self._insert_into_node(self.root, val, None)
    
    def addfrom(self, source):
        """ Inserts all values from iterable source. """
        for val in source:
            self.root = self._insert_into_node(self.root, val, None)
    
    def _skew(self, node):
        if node == None or node.left == None:
            return node
        elif node.left.level == node.level:
            L = node.left
            node.left = L.right
            if L.right:
                L.right.parent = node
                L.right.direction = 'L'
            L.right = node
            L.parent = node.parent
            L.direction = node.direction
            node.parent = L
            node.direction = 'R'
            return L
        else:
            return node
    
    def _split(self, node):
        if node == None or node.right == None or node.right.right == None:
            return node
        elif node.level == node.right.right.level:
            R = node.right
            node.right = R.left
            if R.left:
                R.left.parent = node
                R.left.direction = 'R'
            R.left = node
            R.parent = node.parent
            R.direction = node.direction
            node.parent = R
            node.direction = 'L'
            R.level += 1
            return R
        else:
            return node
    
    def _insert_into_node(self, node, val, parent, direction=None):
        if node == None:
            self._len += 1
            return _sbst_node(val, parent, direction)
        else:
            cmp = self.comp_f(val, node.getval())
            if cmp < 0: # val < node.getval()
                node.left = self._insert_into_node(node.left, val, node, 'L')
            elif cmp > 0: # val > node.getval()
                node.right = self._insert_into_node(node.right, val, node, 'R')
            else: # val == node.getval()
                self._len += 1
                node.addval(val)
                return node
            node = self._skew(node)
            node = self._split(node)
            return node
    
    def forward_from(self, start=None, inclusive=True, \
                     stop=None, stop_incl=False):
        """ Creates and returns generator object which can be used for
          tree traversal in 'forward' direction. Parameters:
        start - starting value. If not specified, tree will be traversed
          from minimal value.
        inclusive - boolean - include or not values that 'equal' to 'start'.
          True (means include) by default.
        stop - value that stops iteration. If not specified, tree will be
          traversed to the end.
        stop_incl - boolean - include or not values that 'equal' to 'stop'.
        
        Default values for 'start' and 'stop' (True for 'inclusive' and False
        for 'stop_incl' respectively) are reminds behavior of 'start' and
        'stop' parameters of 'range' object."""
        node = self.root
        curr = None
        # cumbersome traversal because tree can be rebalanced during iteration
        while node:
            cmp = -1 if start == None else self.comp_f(start, node.getval())
            if cmp == 0:
                if inclusive:
                    curr = node
                    node = None
                else:
                    node = node.right
            elif cmp < 0:
                curr = node
                node = node.left
            else:
                node = node.right
        while curr:
            if curr.len > 0:
                if stop != None:
                    cmp = self.comp_f(curr.getval(), stop)
                    if cmp > 0 or cmp == 0 and not stop_incl:
                        return
                if curr.is_array:
                    i = 0 # 'for' is not used because of possible update of curr.val
                    while i < curr.len:
                        yield curr.val[i]
                        i += 1
                else:
                    yield curr.val
            # step forward
            if curr.right:
                curr = curr.right
                while curr.left:
                    curr = curr.left
            else:
                new_curr = curr.parent
                while new_curr and curr.direction == 'R':
                    curr = new_curr
                    new_curr = curr.parent
                curr = new_curr
    
    def backward_from(self, start=None, inclusive=True, \
                      stop=None, stop_incl=False):
        """ Creates and returns generator object which can be used for
          tree traversal in 'backward' direction. Parameters:
        start - starting value. If not specified, tree will be traversed
          from maximal value.
        inclusive - boolean - include or not values that 'equal' to 'start'.
          True (means include) by default.
        stop - value that stops iteration. If not specified, tree will be
          traversed to the end.
        stop_incl - boolean - include or not values that 'equal' to 'stop'."""
        node = self.root
        curr = None
        while node:
            cmp = 1 if start == None else self.comp_f(start, node.getval())
            if cmp == 0:
                if inclusive:
                    curr = node
                    node = None
                else:
                    node = node.left
            elif cmp > 0:
                curr = node
                node = node.right
            else:
                node = node.left
        while curr:
            if curr.len > 0:
                if stop != None:
                    cmp = self.comp_f(curr.getval(), stop)
                    if cmp < 0 or cmp == 0 and not stop_incl:
                        return
                if curr.is_array:
                    i = 0
                    while i < curr.len:
                        yield curr.val[i]
                        i += 1
                else:
                    yield curr.val
            # step backward
            if curr.left:
                curr = curr.left
                while curr.right:
                    curr = curr.right
            else:
                new_curr = curr.parent
                while new_curr and curr.direction == 'L':
                    curr = new_curr
                    new_curr = curr.parent
                curr = new_curr
    
    def min(self, limit=None, inclusive=True):
        """ Returns minimal value that is not less (if 'inclusive'
        parameter is True) or greater (inclusive=False) than
        specified limit. """
        for val in self.forward_from(limit, inclusive):
            return val
        return None
    
    def max(self, limit=None, inclusive=True):
        """ Returns maximal value that is not greater (if 'inclusive'
        parameter is True) or less (inclusive=False) than specified
        limit. """
        for val in self.backward_from(limit, inclusive):
            return val
        return None
    
    def nodes_list(self):
        """ Returns list of _sbst_node objects. Could be useful
        in some cases."""
        return self._nodes_list(self.root)
    
    def _nodes_list(self, node):
        if not node:
            return []
        else:
            return self._nodes_list(node.left) + [node] \
                   + self._nodes_list(node.right)
    
    # --------- If you don't need 'remove', finish copy-paste here ---------
    
    def remove(self, val, allcopies=False):
        """ Removes value from the tree. Parameters:
        val - value to be removed
        allcopies - boolean - suggests remove all the exact copies of
          specified 'val'. """
        if val != None:
            self.root = self._delete(val, self.root, allcopies)
    
    def _delete(self, val, node, allcopies):
        if node == None:
            return None
        cmp = self.comp_f(val, node.getval())
        if cmp > 0:
            node.right = self._delete(val, node.right, allcopies)
        elif cmp < 0:
            node.left = self._delete(val, node.left, allcopies)
        else:
            node_len_before_deletion = node.len
            node.dropval(val, allcopies)
            self._len -= node_len_before_deletion - node.len
            if node.len == 0:
                if node.left == None and node.right == None:
                    return None
                elif node.left == None: # node.right exists
                    NN = node.right
                    while NN.left:
                        NN = NN.left
                    if NN != node.right:
                        if NN.right:
                            NN.right.parent = NN.parent
                            NN.right.direction = 'L'
                        NN.parent.left = NN.right
                        RN = NN.parent
                        while RN != node:
                            self._decrease_level(RN)
                            RN = RN.parent
                        NN.right = node.right
                        NN.right.parent = NN
                    NN.parent = node.parent
                    NN.direction = node.direction
                    NN.level = node.level
                    node.right = NN
                    node = NN
                else: # node.left exists and node.right maybe too
                    PN = node.left
                    while PN.right:
                        PN = PN.right
                    if PN != node.left:
                        if PN.left:
                            PN.left.parent = PN.parent
                            PN.left.direction = 'R'
                        PN.parent.right = PN.left
                        RN = PN.parent
                        while RN != node:
                            self._decrease_level(RN)
                            RN = RN.parent
                        PN.left = node.left
                        PN.left.parent = PN
                    PN.parent = node.parent
                    PN.direction = node.direction
                    PN.level = node.level
                    PN.right = node.right
                    if PN.right:
                        PN.right.parent = PN
                    node.left = PN
                    node = PN
        self._decrease_level(node)
        return node
    
    def _decrease_level(self, node):
        should_be = max(node.left.level if node.left else 0, \
                        node.right.level if node.right else 0) + 1
        if should_be < node.level:
            node.level = should_be
            if should_be < (node.right.level if node.right else 0):
                node.right.level = should_be

# -------------- Finish copy-paste here --------------

if __name__ == "__main__":
    import doctest
    print('Doctest started...')
    doctest.testmod()
    print('...doctest finished.')
