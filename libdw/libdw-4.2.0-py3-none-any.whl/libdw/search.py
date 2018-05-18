"""
Procedures and classes for doing basic breadth-first and depth-first
search, with and without dynamic programming. 
"""
somewhatVerbose = False
"""If ``True``, prints a trace of the search"""
verbose = False
"""If ``True``, prints a verbose trace of the search"""

class SearchNode:
    """A node in a search tree"""
    def __init__(self, action, state, parent):
        self.state = state
        self.action = action
        """Action that moves from ``parent`` to ``state``"""
        self.parent = parent
        
    def path(self):
        """:returns: list of ``(action, state)`` pairs from root to this node"""
        if self.parent == None:
            return [(self.action, self.state)]
        else:
            return self.parent.path() + [(self.action, self.state)]

    def inPath(self, s):
        """
        :returns: ``True`` if state ``s`` is in the path from here to the root
        """
        if s == self.state:
            return True
        elif self.parent == None:
            return False
        else:
            return self.parent.inPath(s)

    def __repr__(self):
        if self.parent == None:
            return str(self.state)
        else:
            return repr(self.parent) + \
                   "-"+str(self.action)+"->"+str(self.state)

    __str__ = __repr__

class Stack:
    """
    Simple implementation of stack using a Python list.
    """
    def __init__(self):
        """Create a new empty stack"""
        self.data = []
    def push(self, item):
        """Push ``item`` onto the stack."""
        self.data.append(item)
    def pop(self):
        """Return the most recently pushed item that has not yet been popped,
           and removes it from the stack."""
        return self.data.pop()
    def isEmpty(self):
        """Returns ``True`` if the stack is empty and ``False`` otherwise."""
        return self.data == []
    def __str__(self):
        return 'Stack('+str(self.data)+')'

class Queue:
    """
    Simple implementation of queue using a Python list.
    """
    def __init__(self):
        """Create a new empty queue"""
        self.data = []
    def push(self, item):
        """Push ``item`` onto the queue."""
        self.data.append(item)
    def pop(self):
        """Return the oldest item that has not yet been popped,
           and removes it from the queue."""
        return self.data.pop(0)
    def isEmpty(self):
        """Returns ``True`` if the queue is empty and ``False`` otherwise."""
        return self.data == []
    def __str__(self):
        return 'Queue('+str(self.data)+')'

def search(initialState, goalTest, actions, successor,
           depthFirst = False, DP = True, maxNodes = 10000):
    """
    :param initialState: root of the search
    :param goalTest: function from state to Boolean
    :param actions: a list of possible actions
    :param successor: function from state and action to next state
    :param depthFirst: do depth-first search if ``True``, otherwise do
           breadth-first
    :param DP: do dynamic programming if ``True``, otherwise not
    :param maxNodes: kill the search after it expands this many nodes
    :returns: path from initial state to a goal state as a list of
           (action, state) tuples
    """
    if depthFirst:
        agenda = Stack()
    else:
        agenda = Queue()

    startNode = SearchNode(None, initialState, None)
    if goalTest(initialState):
        return startNode.path()
    agenda.push(startNode)
    if DP: visited = {initialState: True}
    count = 1
    while not agenda.isEmpty() and maxNodes > count:
        if verbose: print(("agenda: ", agenda))
        n = agenda.pop()
        if somewhatVerbose or verbose: print(("   expanding: ",  n))
        new_states = []
        for a in actions:
            new_s = successor(n.state, a)
            newN = SearchNode(a, new_s, n)
            if goalTest(new_s):
                # We're done!
                print((count, " states visited"))
                return newN.path()
            elif new_s in new_states:
                # We've already gone from s to new_s
                pass
            elif ((not DP) and n.inPath(new_s)) or \
                  (DP and new_s in visited):
                # We already know a path to new_s
                pass
            elif new_s is None:
                pass
            else:
                # We haven't expanded this state yet;  expand it
                count += 1
                if DP: visited[new_s] = True
                new_states.append(new_s)
                agenda.push(newN)
    print(("Search failed after visiting ", count, " states."))
    if DP: print(('Using DP', len(visited)))
    return None

def depthFirst (initialState, goalTest, actions, successor):
    """See ``search`` documentation"""
    return search(initialState, goalTest, actions, successor,
                   depthFirst=True, DP = False)

def breadthFirst (initialState, goalTest, actions, successor):
    """See ``search`` documentation"""
    return search(initialState, goalTest, actions, successor,
                   depthFirst=False, DP = False)

def depthFirstDP (initialState, goalTest, actions, successor):
    """See ``search`` documentation"""
    return search(initialState, goalTest, actions, successor,
                   depthFirst=True, DP = True)

def breadthFirstDP (initialState, goalTest, actions, successor):
    """See ``search`` documentation"""
    return search(initialState, goalTest, actions, successor,
                   depthFirst=False, DP = True)

def smSearch(smToSearch, initialState = None, goalTest = None, maxNodes = 10000,
             depthFirst = False, DP = True):
   """
   :param smToSearch: instance of ``sm.SM`` defining a search domain;
             ``get_next_values`` is used to determine the successor of a
             state given an action
   :param initialState: initial state for the search;  if not
             provided, will use ``smToSearch.start_state``
   :param goalTest: function that takes a state as an argument and
             returns ``True`` if it is a goal state, and ``False`` otherwise
   :param maxNodes: maximum number of nodes to be searched;  prevents
             runaway searches
   :param depthFirst: if ``True``, use depth first search;  usually not
             a good idea
   :param DP: if ``True``, use dynamic programming; usually a good idea
   :returns: a list of the form ``[(a0, s0), (a1, s1), (a2, s2), ...]``
    where the a's  are legal actions of c{smToSearch} and s's are
    states of that  machine.  ``s0`` is the start state;  the last
    state is a state that satisfies the goal test.  If the
    goal is unreachable (within the search limit), it returns ``None``. 
   """
   if initialState == None:
       initialState = smToSearch.get_start_state()
   if goalTest == None:
       goalTest = smToSearch.done
   return search(initialState, goalTest, smToSearch.legal_inputs,
                 # This returns the next state
                 lambda s, a: smToSearch.get_next_values(s, a)[0],
                 maxNodes = maxNodes,
                 depthFirst=depthFirst, DP=DP)

def pathValid(smToSearch, path):
    """
    :param smToSearch: instance of ``sm.SM`` defining a search domain
    :param path: list of the form ``[(a0, s0), (a1, s1), (a2, s2), ...]``
     where the ``a``'s  are legal actions of c{smToSearch} and ``s``'s are
     states of that  machine.
    :returns: ``True`` if taking action a1 in state s0 results in state
     s1, taking action a2 in state s1 results in state s2, etc.  That
     is, if this path through the state space is executable in this
     state machine.
    """
    if len(path) <= 1:
        return True
    else:
        (a0, s0) = path[0]
        (a1, s1) = path[1]
        (resultingS, out) = smToSearch.get_next_values(s0, a1)
        return s1 == resultingS and pathValid(smToSearch, path[1:])
