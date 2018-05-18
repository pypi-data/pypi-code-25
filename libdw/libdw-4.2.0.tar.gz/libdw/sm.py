
"""
Classes for representing and combining state machines.
"""
import copy
import sys
import types
import inspect
from . import util
from functools import reduce

from importlib import reload
reload(util) # TODO: Is this required?

class SM:
    """
    Generic superclass representing state machines.  Don't instantiate
    this:  make a subclass with definitions for the following methods:

        - ``get_next_values: (state_t, inp_t) -> (state_t+1, output_t)`` or
          ``get_next_state: (state_t, inpt_t) -> state_t+1``
        - ``start_state:  state`` or ``start_state() -> state``

    optional:

        - ``done: (state) -> boolean``  (defaults to always false)
        - ``legal_inputs: list(inp)``

    See State Machines chapter in 6.01 Readings for detailed explanation.
    """
    start_state = None
    """By default, start_state is none"""

    def get_start_state(self):
        """
        Handles the case that self.start_state is a function.
        Necessary for stochastic state machines. Ignore otherwise.
        """
        if isinstance(self.start_state, types.MethodType):
            return self.start_state()
        else:
            return self.start_state

    def get_next_values(self, state, inp):
        """
        Default version of this method.  If a subclass only defines
        ``get_next_state``, then we assume that the output of the machine
        is the same as its next state.
        """
        next_state = self.get_next_state(state, inp)
        return (next_state, next_state)

    def done(self, state):
        """
        By default, machines don't terminate
        """
        return False

    def is_done(self):
        """
        Should only be used by transduce.  Don't call this.
        """
        return self.done(self.state)

    legal_inputs = []
    """
    By default, the space of legal inputs is not defined.
    """

    __debug_params = None # internal use
    
    def start(self, trace_tasks = [], verbose = False,
              compact = True, print_input = True):
        """
        Call before providing inp to a machine, or to reset it.
        Sets self.state and arranges things for tracing and debugging.

        :param trace_tasks: list of trace tasks.  See documentation for
         ``do_trace_tasks`` for details
        :param verbose: If ``True``, print a description of each step
         of the machine
        :param compact: If ``True``, then if ``verbose = True``, print a
         one-line description of the step;  if ``False``, print
         out the recursive substructure of the state update at
         each step
        :param print_input: If ``True``, then if ``verbose = True``,
         print the whole input in each step, otherwise don't.
         Useful to set to ``False`` when the input is large and
         you don't want to see it all.
        """
        self.state = self.get_start_state()
        """ Instance variable set by start, and updated by step;
              should not be managed by user """
        self.__debug_params = debug_params(trace_tasks, verbose, compact,
                                         print_input)
        
    def step(self, inp):
        """
        Execute one 'step' of the machine, by propagating ``inp`` through
        to get a result, then updating ``self.state``.
        Error to call ``step`` if ``done`` is true.
        :param inp: next input to the machine
        """
        (s, o) = self.get_next_values(self.state, inp)

        if self.__debug_params and self.__debug_params.do_debugging:
            if self.__debug_params.verbose and not self.__debug_params.compact:
                print("Step:", self.__debug_params.k)
            self.print_debug_info(0, self.state, s, inp, o, self.__debug_params)
            if self.__debug_params.verbose and self.__debug_params.compact:
                if self.__debug_params.print_input:
                    print("In:", inp, "Out:", o, "Next State:", s)
                else:
                    print("Out:", o, "Next State:", s)
            self.__debug_params.k += 1

        self.state = s
        return o

    def transduce(self, inps, verbose = False, trace_tasks = [],
                  compact = True, print_input = True,
                  check = False):
        """
        Start the machine fresh, and feed a sequence of values into
        the machine, collecting the sequence of outputs

    For debugging, set the optional parameter check = True to (partially) 
    check the representation invariance of the state machine before running 
    it.  See the documentation for the ``check`` method for more information
    about what is tested.

        See documentation for the ``start`` method for description of
        the rest of the parameters.
        
        :param inps: list of inputs appropriate for this state machine
        :return: list of outputs
        """
        if check:
            self.check(inps)
        i = 0
        n = len(inps)
        result = []
        self.start(verbose = verbose, compact = compact,
                   print_input = print_input, trace_tasks = trace_tasks)
        if verbose:
            print("Start state:", self.state)
        # Consider stopping if next state is done?  (as it is, we get
        # an output associated with a transition into a done state)
        while i < n and not self.is_done():
            result.append(self.step(inps[i]))
            i = i + 1
            if i % 100 == 0 and verbose:
                print('Step', i)
        return result

    def run(self, n = 10, verbose = False, trace_tasks = [],
                   compact = True, print_input = True, check = False):
        """
        For a machine that doesn't consume input (e.g., one made with
        ``feedback``, for ``n`` steps or until it terminates. 

        See documentation for the ``start`` method for description of
        the rest of the parameters.
        
        :param n: number of steps to run
        :return: list of outputs
        """
        return self.transduce([None]*n, verbose = verbose,
                              trace_tasks = trace_tasks, compact = compact,
                              print_input = print_input,
                              check = check)

    def transduce_f(self, inp_fn, n = 10, verbose = False,
                   trace_tasks = [],
                   compact = True, print_input = True):
        """
        Like ``transduce``, but rather than getting inputs from a list
        of values, get them by calling a function with the input index
        as the argument. 
        """
        return self.transduce([inp_fn(i) for i in range(n)], 
                              trace_tasks = trace_tasks, compact = compact,
                              print_input = print_input, verbose =
                   verbose)
    
    name = None
    """Name used for tracing"""

    def guarantee_name(self):
        """
        Makes sure that this instance has a unique name that can be
        used for tracing.
        """
        if not self.name:
            self.name = util.gensym(self.__class__.__name__)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        """
        Default method for printing out all of the debugging
        information for a primitive machine.
        """
        self.guarantee_name()
        if debug_params.verbose and not debug_params.compact:
            if debug_params.print_input:
                print(' '*depth, self.name, "In:", \
                      util.pretty_string(inp), \
                      "Out:", util.pretty_string(out), \
                      "Next State:", util.pretty_string(next_state))
            else:
                print(' '*depth, self.name, \
                      "Out:", util.pretty_string(out), \
                      "Next State:", util.pretty_string(next_state))
        self.do_trace_tasks(inp, state, out, debug_params)

    def do_trace_tasks(self, inp, state, out, debug_params):
        """
        Actually execute the trace tasks.  A trace task is a list
        consisting of three components:

            - ``name``: is the name of the machine to be traced
            - ``mode``: is one of ``'input'``, ``'output'``, or ``'state'``
            - ``fun``: is a function

        To **do** a trace task, we call the function ``fun`` on the
        specified attribute of the specified mahine.  In particular,
        we execute it right now if its machine name equals the name of
        this machine.
        """
        for (name, mode, fun) in debug_params.trace_tasks:
            if name == self.name:
                if mode == 'input':
                    fun(inp)
                elif mode == 'state':
                    fun(state)
                else:
                    fun(out)

    def check(thesm, inps = None):
        """
        Run a rudimentary check on a state machine, using the list of inputs provided.
        Makes sure that get_next_values is defined, and that it takes the proper number
        of input arguments (three: self, start, inp).  Also print out the start state,
        and check that get_next_values provides a legal return value (list of 2 elements:
        (state,output)).  And tries to check if get_next_values is changing either self.state
        or some other attribute of the state machine instance (it shouldn't: get_next_values
        should be a pure function).

        Raises exception 'InvalidSM' if a problem is found.

            :param thesm: the state machine instance to check
            :param inps: list of inputs to test the state machine on (default None)
            :return: none

            """
            # see if get_next_values is defined and is not the default version
        # note that hasattr(thesm,'get_next_values') is always True, because
        # get_next_values is defined in sm.SM
        #
        # so let's do this in an ugly way, by checking the documentation string
        # for get_next_values, and seeing if that starts with "Default version"
        gnvdoc = inspect.getdoc(thesm.get_next_values)
        if gnvdoc != None:
            if len(gnvdoc)>16:
                if gnvdoc[:15]=='Default version':
                    print("[SMCheck] Error! get_next_values undefined in state machine")
                    if hasattr(thesm,'GetNextValues'):
                        print("[SMCheck] you've defined GetNextValues -> should be get_next_values")
                    if hasattr(thesm,'get_next_state'):
                        print("[SMCheck] you've defined get_next_state -> should be get_next_values?")
                    raise Exception('Invalid SM')
            
            # check arguments of get_next_values
            aspec = inspect.getargspec(thesm.get_next_values)
            if isinstance(aspec, tuple):
                args = aspec[0]
            else:
                args = aspec.args
            if not (len(args)==3):
                print("[SMCheck] get_next_values should take 3 arguments as input, namely self, state, inp")
                print("          your function takes the arguments ",args)
                raise Exception('Invalid SM')

            # check start state
            ss = thesm.start_state
            # start the machine (needed if complex, like cascade)
            thesm.start()
            print("[SMCheck] the start state of your state machine is '%s'" % repr(ss))
            # check if get_next_values return value is legal
            if inps != None:
                rv = thesm.get_next_values(thesm.state,inps[0])
                if not type(rv) in (list, tuple):
                    print("[SMCheck] get_next_values provides an invalid return value, '%s'" % repr(rv))
                    raise Exception('Invalid SM')
                if not(len(rv)==2):
                    print("[SMCheck] get_next_values provides an invalid return value, '%s'" % repr(rv))
                    print("[SMCheck] the return value length should be 2, ie (state,output), but it is ",len(rv))
                    raise Exception('Invalid SM')


            # Test to see if we're side-effecting the state.  This is not
            # foolproof: it might miss some cases of state side-effects
            start_state_copy = copy.copy(thesm.start_state)
            attrs = inspect.getmembers(thesm)
            original_attrs = dict(copy.copy(attrs))
            # Call get_next_values a bunch of times
            thesm.start()
            for i in inps:
                thesm.get_next_values(thesm.state, i)
            # See what got clobbered
            if thesm.state != start_state_copy:
                print("[SMCheck] Your get_next_values method changes self.state.  It should instead return the new state as the first component of the result")
                raise Exception('Invalid SM')
            new_attrs = dict(inspect.getmembers(thesm))
            for (name, val) in list(original_attrs.items()):
                if name != '_SM__debug_params' and new_attrs[name] != val:
                    print('[SMCheck] You seem to have changed attribute', end=' ')
                    print(name, 'from', val, 'to', new_attrs[name])
                    print('[SMCheck] but the get_next_values should not have side effects')
                    raise Exception('Invalid SM')
                
            # print "[SMCheck] Ok - your state machine passed this (rudimentary) check!"

                    
                    
######################################################################
#    Compositions
######################################################################

class Cascade (SM):
    """
    Cascade composition of two state machines.  The output of ``sm1``
    is the input to ``sm2``
    """
    def __init__(self, m1, m2, name = None):
        """
        :param m1: ``SM``
        :param m2: ``SM``
        """
        self.m1 = m1
        self.m2 = m2
        if not ((name is None or isinstance(name, str)) and isinstance(m1, SM) and isinstance(m2, SM)):
            print(m1, m2, name)
            raise Exception('Cascade takes two machine arguments and an optional name argument')
        self.name = name
        self.legal_inputs = self.m1.legal_inputs

    def start_state(self):
        return (self.m1.get_start_state(), self.m2.get_start_state())

    def get_next_values(self, state, inp):
        (s1, s2) = state
        (new_s1, o1) = self.m1.get_next_values(s1, inp)
        (new_s2, o2) = self.m2.get_next_values(s2, o1)
        return ((new_s1, new_s2), o2)

    def done(self, state):
        (s1, s2) = state
        return self.m1.done(s1) or self.m2.done(s2)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name)
            (s1, s2) = state
            (ns1, ns2) = next_state
            (ns1, o1) = self.m1.get_next_values(s1, inp)
            self.m1.print_debug_info(depth + 4, s1, ns1, inp, o1, debug_params)
            self.m2.print_debug_info(depth + 4, s2, ns2, o1, out, debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)

class Parallel (SM):
    """
    Takes a single inp and feeds it to two machines in parallel.
    Output of the composite machine is the pair of outputs of the two
    individual machines.
    """

    def __init__(self, m1, m2, name = None):
        self.m1 = m1
        self.m2 = m2
        if not ((name is None or isinstance(name, str)) and isinstance(m1, SM) and isinstance(m2, SM)):
            raise Exception('Parallel takes two machine arguments and an optional name argument')
        self.name = name
        # Legal inputs to this machine are the legal inputs to the first
        # machine (which had better equal the legal inputs to the second
        # machine).  Check that here.
        assert set(self.m1.legal_inputs) == set(self.m2.legal_inputs)
        self.legal_inputs = self.m1.legal_inputs

    def start_state(self):
        return (self.m1.get_start_state(), self.m2.get_start_state())

    def get_next_values(self, state, inp):
        (s1, s2) = state
        (new_s1, o1) = self.m1.get_next_values(s1, inp)
        (new_s2, o2) = self.m2.get_next_values(s2, inp)
        return ((new_s1, new_s2), (o1, o2))

    def done(self, state):
        (s1, s2) = state
        return self.m1.done(s1) or self.m2.done(s2)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (s1, s2) = state
            (ns1, ns2) = next_state
            (o1, o2) = out
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name)
            self.m1.print_debug_info(depth + 4, s1, ns1, inp, o1, debug_params)
            self.m2.print_debug_info(depth + 4, s2, ns2, inp, o2, debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)


class Feedback (SM):
    """
    Take the output of ``m`` and feed it back to its input.  Resulting
    machine has no input.  The output of ``m`` **must not** depend on
    its input without a delay.
    """
    def __init__(self, m, name = None):
        self.m = m
        if not ((name is None or isinstance(name, str)) and isinstance(m, SM)):
            raise Exception('Feedback takes one machine argument and an optional name argument')
        self.name = name

    def start_state(self):
        return self.m.get_start_state()

    def get_next_values(self, state, inp):
        """
        Ignores input.
        """
        # Will only compute output
        (ignore, o) = self.m.get_next_values(state, 'undefined')
        assert o != 'undefined', 'Error in feedback; machine has no delay'
        # Will only compute next state
        (new_s, ignore) = self.m.get_next_values(state, o)
        return (new_s, o)

    def done(self, state):
        return self.m.done(state)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        (machine_state, last_output) = self.get_next_values(state, inp)
        self.guarantee_name()
        if debug_params.verbose and not debug_params.compact:
            print(' '*depth, self.name)
        self.m.print_debug_info(depth + 4, state, next_state,
                              last_output, out, debug_params)
        self.do_trace_tasks(inp, state, out, debug_params)

def coupled_machine(m1, m2):
    """
    Couple two machines together.
    :param m1: ``SM``
    :param m2: ``SM``
    :returns: New machine with no input, in which the output of ``m1``
    is the input to ``m2`` and vice versa.
    """
    return Feedback(Cascade(m1, m2))

class Feedback2 (Feedback):
    """
    Like previous ``Feedback``, but takes a machine with two inps and 
    one output at initialization time.  Feeds the output back to the
    second inp.  Result is a machine with a single inp and single
    output.  
    """
    def get_next_values(self, state, inp):
        # Will only compute output
        (ignore, o) = self.m.get_next_values(state, (inp, 'undefined'))
        assert o != 'undefined', 'Error in feedback; machine has no delay'
        # Will only compute next state
        (new_s, ignore) = self.m.get_next_values(state, (inp, o))
        return (new_s, o)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        (machine_state, last_output) = self.get_next_values(state,
                                                        (inp, 'undefined'))
        self.guarantee_name()
        if debug_params.verbose and not debug_params.compact:
            print(' '*depth, self.name)
        self.m.print_debug_info(depth + 4, state, next_state,
                              (inp, last_output), out, debug_params)
        self.do_trace_tasks(inp, state, out, debug_params)

class FeedbackAdd(SM):
    """
    Takes two machines, m1 and m2.  Output of the composite machine is
    the output to m1.  Output of m1 is fed back through m2;  that
    result is added to the input and used as the 'error'
    signal, which is the input to m1.  
    """
    def __init__(self, m1, m2, name = None):
        self.m1 = m1
        self.m2 = m2
        if not ((name is None or isinstance(name, str)) and isinstance(m1, SM) and isinstance(m2, SM)):
            raise Exception('FeedbackAdd takes two machine arguments and an optional name argument')
        self.name = name

    def start_state(self):
        # Start state is product of start states of the two machines
        return (self.m1.get_start_state(), self.m2.get_start_state())
        
    def get_next_values(self, state, inp):
        (s1, s2) = state
        # All this craziness is to deal with the fact that either m1
        # or m2 might have immediate dependence on the input.  If both
        # do, then it's an error.

        # Propagate the input through, so we're sure about the input
        # to m1
        (ignore, o1) = self.m1.get_next_values(s1, 99999999)
        (ignore, o2) = self.m2.get_next_values(s2, o1)
        # Now get a real new state and output
        (new_s1, output) = self.m1.get_next_values(s1, safeAdd(inp,o2))
        (new_s2, o2) = self.m2.get_next_values(s2, output)
        return ((new_s1, new_s2), output)

    def done(self, state):
        (s1, s2) = state
        return self.m1.done(s1) or self.m2.done(s2)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (s1, s2) = state
            (ns1, ns2) = next_state
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name)
            # Only way to do this right is to call machines again
            (ignore, o1) = self.m1.get_next_values(s1, inp)
            (ignore, o2) = self.m2.get_next_values(s2, o1)
            (ignore, o1) = self.m1.get_next_values(s1, inp+o2)
            self.m1.print_debug_info(depth + 4, s1, ns1, inp+o2, o1, debug_params)
            self.m2.print_debug_info(depth + 4, s2, ns2, o1, o2, debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)


class FeedbackSubtract(SM):
    """
    Takes two machines, m1 and m2.  Output of the composite machine is
    the output to m1.  Output of m1 is fed back through m2;  that
    result is subtracted from the input and used as the 'error'
    signal, which is the input to m1.  Transformation is the one
    described by Black's formula.
    """
    def __init__(self, m1, m2, name = None):
        self.m1 = m1
        self.m2 = m2
        if not ((name is None or isinstance(name, str)) and isinstance(m1, SM) and isinstance(m2, SM)):
            raise Exception('FeedbackSubtract takes two machine arguments and an optional name argument')
        self.name = name

    def start_state(self):
        # Start state is product of start states of the two machines
        return (self.m1.get_start_state(), self.m2.get_start_state())
        
    def get_next_values(self, state, inp):
        (s1, s2) = state
        # All this craziness is to deal with the fact that either m1
        # or m2 might have immediate dependence on the input.  If both
        # do, then it's an error.

        # Propagate the input through, so we're sure about the input
        # to m1
        (ignore, o1) = self.m1.get_next_values(s1, 99999999)
        (ignore, o2) = self.m2.get_next_values(s2, o1)
        # Now get a real new state and output
        (new_s1, output) = self.m1.get_next_values(s1, inp - o2)
        (new_s2, o2) = self.m2.get_next_values(s2, output)
        return ((new_s1, new_s2), output)

    def done(self, state):
        (s1, s2) = state
        return self.m1.done(s1) or self.m2.done(s2)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (s1, s2) = state
            (ns1, ns2) = next_state
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name)
            # Only way to do this right is to call machines again
            (ignore, o1) = self.m1.get_next_values(s1, inp)
            (ignore, o2) = self.m2.get_next_values(s2, o1)
            (ignore, o1) = self.m1.get_next_values(s1, inp - o2)
            self.m1.print_debug_info(depth + 4, s1, ns1, inp-o2, o1, debug_params)
            self.m2.print_debug_info(depth + 4, s2, ns2, o1, o2, debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)



class Parallel2 (Parallel):
    """
    Like ``Parallel``, but takes two inps.
    Output of the composite machine is the pair of outputs of the two
    individual machines.
    """
    def __init__(self, m1, m2):
        Parallel.__init__(self, m1, m2)
        # Legal inputs to this machine are the cartesian product of the
        # legal inputs to both machines
        self.legal_inputs =  [(i1, i2) for i1 in self.m1.legal_inputs \
                             for i2 in self.m2.legal_inputs]
    
    def get_next_values(self, state, inp):
        (s1, s2) = state
        (i1, i2) = split_value(inp)
        (new_s1, o1) = self.m1.get_next_values(s1, i1)
        (new_s2, o2) = self.m2.get_next_values(s2, i2)
        return ((new_s1, new_s2), (o1, o2))

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (s1, s2) = state
            (ns1, ns2) = next_state
            (i1, i2) = split_value(inp)
            (o1, o2) = out
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name)
            self.m1.print_debug_info(depth + 4, s1, ns1, i1, o1, debug_params)
            self.m2.print_debug_info(depth + 4, s2, ns2, i2, o2, debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)


class ParallelAdd (Parallel):
    """
    Like ``Parallel``, but output is the sum of the outputs of the two
    machines. 
    """
    def get_next_values(self, state, inp):
        (s1, s2) = state
        (new_s1, o1) = self.m1.get_next_values(s1, inp)
        (new_s2, o2) = self.m2.get_next_values(s2, inp)
        return ((new_s1, new_s2), o1 + o2)

class If (SM):
    """
    Given a condition (function from inps to boolean) and two state
    machines, make a new machine.  The condition is evaluated at start
    time, and one machine is selected, permanently, for execution.

    Rarely useful.
    """
    start_state = ('start', None)
    
    def __init__(self, condition, sm1, sm2, name = None):
        """
        :param condition: ``Procedure`` mapping ``inp`` -> ``Boolean``
        :param sm1: ``SM``
        :param sm2: ``SM``
        """
        self.sm1 = sm1
        self.sm2 = sm2
        self.condition = condition
        if not ((name is None or isinstance(name, str)) and isinstance(sm1, SM) and isinstance(sm2, SM)):
            raise Exception('If takes a condition, two machine arguments and an optional name argument')
        self.name = name
        self.legal_inputs = self.sm1.legal_inputs

    def get_first_real_state(self, inp):
        # State is boolean indicating which machine is running, and its state
        if self.condition(inp):
            return ('runningM1', self.sm1.get_start_state())
        else:
            return ('runningM2', self.sm2.get_start_state())

    def get_next_values(self, state, inp):
        (if_state, sm_state) = state
        if if_state == 'start':
            (if_state, sm_state) = self.get_first_real_state(inp)
        
        if if_state == 'runningM1':
            (new_s, o) = self.sm1.get_next_values(sm_state, inp)
            return (('runningM1', new_s), o)
        else:
            (new_s, o) = self.sm2.get_next_values(sm_state, inp)
            return (('runningM2', new_s), o)

    def done(self, state):
        (if_state, sm_state) = state
        if if_state == 'start':
            return False
        elif if_state == 'runningM1':
            return self.sm1.done(sm_state)
        else:
            return self.sm2.done(sm_state)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (if_state, sm_state) = state
            (nif_state, nsm_state) = next_state
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name, if_state)
            if if_state == 'runningM1':
                self.sm1.print_debug_info(depth + 4, sm_state, nsm_state,
                                        inp, out, debug_params)
            elif if_state == 'runningM2':
                self.sm2.print_debug_info(depth + 4, sm_state, nsm_state,
                                        inp, out, debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)

class Switch (SM):
    """
    Given a condition (function from inps to boolean) and two state
    machines, make a new machine.  The condition is evaluated on every
    step, and the selected machine is used to generate output and has
    its state updated.  If the condition is true, ``sm1`` is used, and
    if it is false, ``sm2`` is used.
    """
    def __init__(self, condition, sm1, sm2, name = None):
        """
        :param condition: ``Procedure`` mapping ``inp`` -> ``Boolean``
        :param sm1: ``SM``
        :param sm2: ``SM``
        """
        self.m1 = sm1
        self.m2 = sm2
        self.condition = condition
        if not ((name is None or isinstance(name, str)) and isinstance(sm1, SM) and isinstance(sm2, SM)):
            raise Exception('Switch takes a condition, two machine arguments and an optional name argument')
        self.name = name
        self.legal_inputs = self.m1.legal_inputs

    def start_state(self):
        return (self.m1.get_start_state(), self.m2.get_start_state())

    def get_next_values(self, state, inp):
        (s1, s2) = state
        if self.condition(inp):
            (ns1, o) = self.m1.get_next_values(s1, inp)
            return ((ns1, s2), o)
        else:
            (ns2, o) = self.m2.get_next_values(s2, inp)
            return ((s1, ns2), o)

    def done(self, state):
        (s1, s2) = state
        return self.m1.done(s1) or self.m2.done(s2)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (s1, s2) = state
            (ns1, ns2) = next_state
            if self.condition(inp):
                machine_running = 'M1'
            else:
                machine_running = 'M2'
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name, 'Running', machine_running)
            if machine_running == 'M1':
                self.m1.print_debug_info(depth + 4, s1, ns1, inp, out,debug_params)
            else:
                self.m2.print_debug_info(depth + 4, s2, ns2, inp, out,debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)

class Mux (Switch):
    """
    Like ``Switch``, but updates both machines no matter whether the
    condition is true or false.  Condition is only used to decide
    which output to generate.  If the condition is true, it generates
    the output from the first machine, otherwise, from the second.
    """
    def get_next_values(self, state, inp):
        (s1, s2) = state
        (ns1, o1) = self.m1.get_next_values(s1, inp)
        (ns2, o2) = self.m2.get_next_values(s2, inp)
        if self.condition(inp):
            return ((ns1, ns2), o1)
        else:
            return ((ns1, ns2), o2)

######################################################################
#    
#    Terminating State Machines
#
######################################################################

class Sequence (SM):
    """
    Given a list of state machines, make a new machine that will execute
    the first until it is done, then execute the second, etc.  Assume
    they all have the same input space.
    """
    def __init__(self, sm_list, name = None):
        """
        :param sm_list: ``List`` of terminating ``SM``
        """
        self.sm_list = sm_list
        if not (name is None or isinstance(name, str)) or not isinstance(sm_list, (tuple, list)):
            raise Exception('Sequence takes a list of machines and an optional name argument')
        self.n = len(sm_list)
        self.name = name
        self.legal_inputs = self.sm_list[0].legal_inputs

    def start_state(self):
        return self.advance_if_done(0, self.sm_list[0].get_start_state())

    def advance_if_done(self, counter, sm_state):
        """
        Internal use only.
        If that machine is done, start new machines until we get to
        one that isn't done
        """
        while self.sm_list[counter].done(sm_state) and counter + 1 < self.n:
            # This machine is done and there's another left in the sequence
            counter = counter + 1
            sm_state = self.sm_list[counter].get_start_state()
        return (counter, sm_state)
    
    def get_next_values(self, state, inp):
        (counter, sm_state) = state
        # Get new stuff for current machine on the list
        (sm_state, o) = self.sm_list[counter].get_next_values(sm_state, inp)
        # Start new machines until we get a good one or we finish 
        (counter, sm_state) = self.advance_if_done(counter, sm_state)
        return ((counter, sm_state), o)

    def done(self, state):
        # This machine is done if its current machine is done
        (counter, sm_state) = state
        return self.sm_list[counter].done(sm_state)

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        # This condition is trying to guarantee that next_state has the
        # right structure to be passed down recursively
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (counter, sm_state) = state
            (ncounter, nsm_state) = next_state
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name, 'Counter =', counter)
            self.sm_list[counter].print_debug_info(depth + 4, sm_state, nsm_state,
                                                inp, out, debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)

class Repeat (SM):
    """
    Given a terminating state machine, generate a new one that will
    execute it n times.  If n is unspecified, it will repeat forever.
    """
    def __init__(self, sm, n = None, name = None):
        """
        :param sm: terminating ``SM``
        :param n: positive integer
        """
        self.sm = sm
        self.n = n
        if not ((name is None or isinstance(name, str)) and isinstance(sm, SM)):
            raise Exception('Repeast takes one machine argument, an integer, and an optional name argument')
        self.name = name
        self.legal_inputs = self.sm.legal_inputs

    def start_state(self):
        return self.advance_if_done(0, self.sm.get_start_state())

    def advance_if_done(self, counter, sm_state):
        while self.sm.done(sm_state) and not self.done((counter, sm_state)):
            counter = counter + 1
            print('Repeat counter', counter)
            sm_state = self.sm.get_start_state()
        return (counter, sm_state)

    def get_next_values(self, state, inp):
        (counter, sm_state) = state
        (sm_state, o) = self.sm.get_next_values(sm_state, inp)
        (counter, sm_state) = self.advance_if_done(counter, sm_state)
        return ((counter, sm_state), o)

    # We're done if the termination condition is defined and met
    def done(self, state):
        (counter, sm_state) = state
        return not self.n == None and counter == self.n

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (counter, sm_state) = state
            (ncounter, nsm_state) = next_state
            if debug_params.verbose and not debug_params.compact:        
                print(' '*depth, self.name, 'Counter =', counter)
            self.sm.print_debug_info(depth + 4, sm_state, nsm_state, inp, out,
                                   debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)

class RepeatUntil (SM):
    """
    Given a terminating state machine and a condition on the input,
    generate a new one that will run the machine until the condition
    becomes true.  However, the condition is **only** evaluated when
    the sub-machine terminates.
    """
    def __init__(self, condition, sm, name = None):
        """
        :param condition: ``Procedure`` mappin ``input`` to ``Boolean``
        :param sm: terminating ``SM``
        """
        self.sm = sm
        self.condition = condition
        if not ((name is None or isinstance(name, str)) and isinstance(sm, SM)):
            raise Exception('RepeatUntil takes a condition, a machine argument and an optional name argument')
        self.name = name
        self.legal_inputs = self.sm.legal_inputs

    def start_state(self):
        return (False, self.sm.get_start_state())

    def get_next_values(self, state, inp):
        (cond_true, sm_state) = state
        (sm_state, o) = self.sm.get_next_values(sm_state, inp)
        cond_true = self.condition(inp)
        # child machine is done, but the whole machine is not
        if self.sm.done(sm_state) and not cond_true:
            # Restart the child machine.  Could check to see if it's
            # done, but if the child machine wakes up done and our
            # condition is not true, then we'd risk an infinite loop.
            sm_state = self.sm.get_start_state()
        return ((cond_true, sm_state), o)

    def done(self, state):
        # We're done if component machine is done and the termination
        # condition is true
        (cond_true, sm_state) = state
        return self.sm.done(sm_state) and cond_true
    
    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (cond_true, sm_state) = state
            (ncond_true, nsm_state) = next_state
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name, 'Condition =', cond_true)
            self.sm.print_debug_info(depth + 4, sm_state, nsm_state, inp, out,
                                   debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)

class Until (SM):
    """
    Execute SM until it terminates or the condition becomes true.
    Condition is evaluated on the inp
    """
    def __init__(self, condition, sm, name = None):
        """
        :param condition: ``Procedure`` mappin ``input`` to ``Boolean``
        :param sm: terminating ``SM``
        """
        self.sm = sm
        self.condition = condition
        if not ((name is None or isinstance(name, str)) and isinstance(sm, SM)):
            raise Exception('Until takes a condition, a machine arguments and an optional name argument')
        self.name = name
        self.legal_inputs = self.sm.legal_inputs

    def start_state(self):
        return (False, self.sm.get_start_state())

    def get_next_values(self, state, inp):
        (cond_true, sm_state) = state
        (sm_state, o) = self.sm.get_next_values(sm_state, inp)
        return ((self.condition(inp), sm_state), o)
    
    def done(self, state):
        (cond_true, sm_state) = state
        return self.sm.done(sm_state) or cond_true

    def print_debug_info(self, depth, state, next_state, inp, out, debug_params):
        if next_state and len(next_state) == 2:
            self.guarantee_name()
            (cond_true, sm_state) = state
            (ncond_true, nsm_state) = next_state
            if debug_params.verbose and not debug_params.compact:
                print(' '*depth, self.name,'Condition =', cond_true)
            self.sm.print_debug_info(depth + 4, sm_state, nsm_state, inp, out,
                                   debug_params)
            self.do_trace_tasks(inp, state, out, debug_params)
        

#############################################################################
##   Utility stuff
#############################################################################

def split_value(v, n = 2):
    """
    If ``v`` is a list of ``n`` elements, return it; if it is
    'undefined', return a list of ``n`` 'undefined' values; else
    generate an error
    """
    if v == 'undefined':
        return ['undefined']*n
    else:
        assert len(v) == n, "Value wrong length"
        return v

class debug_params:
    """
    Housekeeping stuff
    """
    def __init__(self, trace_tasks, verbose, compact, print_input):
        self.trace_tasks = trace_tasks
        self.verbose = verbose
        self.compact = compact
        self.print_input = print_input
        self.do_debugging = verbose or len(trace_tasks) > 0
        self.k = 0

#############################################################################
##   Some very simple machines that are broadly useful
#############################################################################

class Wire(SM):
    """
    Machine whose output is its input, with no delay
    """
    def get_next_state(self, state, inp):
        return inp

class Constant(SM):
    """
    Machine whose output is a constant, independent of the input
    """
    def __init__(self, c):
        """
        :param c: constant value
        """
        self.c = c
    def get_next_state(self, state, inp):
        return self.c

class R(SM):
    """
    Machine whose output is the input, but delayed by one time step.
    Specify initial output in initializer.
    """
    def __init__(self, v0 = 0):
        """
        :param v0: initial output value
        """
        self.start_state = v0
        """State is the previous input"""
    def get_next_values(self, state, inp):
        # new state is inp, current output is old state
        return (inp, state)

Delay = R
"""Delay is another name for the class R, for backward compatibility"""

class Gain(SM):
    """
    Machine whose output is the input, but multiplied by k.
    Specify k in initializer.
    """
    def __init__(self, k):
        """
        :param k: gain
        """
        self.k = k
    def get_next_values(self, state, inp):
        # new state is inp, current output is old state
        return (state, safeMul(self.k, inp))

class Wire(SM):
    """Machine whose output is the input"""
    def get_next_values(self, state, inp):
        return (state, inp)

class Select (SM):
    """
    Machine whose input is a structure list and whose output is the
    ``k`` th element of that list.
    """
    def __init__(self, k):
        """
        :param k: positive integer describing which element of input
        structure to select
        """
        self.k = k
    def get_next_state(self, state, inp):
        return inp[self.k]

class PureFunction(SM):
    """
    Machine whose output is produced by applying a specified Python
    function to its input.
    """
    def __init__(self, f):
        """
        :param f: a function of one argument
        """
        self.f = f
    def get_next_values(self, state, inp):
        return (None, self.f(inp))

import operator

######################################################################
##
##  To work in feedback situations we need to propagate 'undefined'
##  through various operations. 

def is_defined(v):
    return not v == 'undefined'
def all_defined(struct):
    if struct == 'undefined':
        return False
    elif isinstance(struct, list) or isinstance(struct, tuple):
        return reduce(operator.and_, [all_defined(x) for x in struct])
    else:
        return True

# Only binary functions for now
def safe(f):
    def safef(a1, a2):
        if all_defined(a1) and all_defined(a2):
            return f(a1, a2)
        else:
            return 'undefined'
    return safef

safeAdd = safe(operator.add)
safeMul = safe(operator.mul)
safeSub = safe(operator.sub)
    
