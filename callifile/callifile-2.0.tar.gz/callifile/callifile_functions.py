import inspect
from inspect import getargspec
from printind.printind_function import printi, printiv
import fnmatch


def callifile(module=None, verbose=False, pattern_to_call=None):
    """Call all the functions in a given module or file. Call only function that
    can be called without arguments or with default arguments.

    - module: the module / file on which call all functions. If None (default), take
        the caller one's.
    - verbose: True / False (default False)
    - pattern_to_call: call only functions that fit pattern_to_call. Default
        None (call all independantly of pattern matching, except a few specific
        self-recursive names)."""

    if module is None:
        frm = inspect.stack()[1]
        module = inspect.getmodule(frm[0])

    if verbose:
        printi("Apply call_all_function_in_this_file on {}".format(module))

    if verbose:
        if pattern_to_call is not None:
            printiv(pattern_to_call)

    all_functions = inspect.getmembers(module, inspect.isfunction)

    for key, value in all_functions:

        if verbose:
            printi("See if should call {} ...".format(key))

        # check if can be called without argument ------------------------------
        getargspec_output = getargspec(value)
        number_arguments = len(getargspec_output.args)
        if getargspec_output.defaults is None:
            number_default_arguments = 0
        else:
            number_default_arguments = len(getargspec_output.defaults)

        if (number_arguments > number_default_arguments):
            if verbose:
                printi("discard {} because of arguments numbers!".format(key))
            continue

        # check if it is this function -----------------------------------------
        if (key == "call_all_function_in_this_file"):
            if verbose:
                printi("discard {} because function itself!".format(key))
            continue

        # check if it is from callifile module ---------------------------------
        if fnmatch.fnmatch(key, "*callifile*"):
            if verbose:
                printi("discard {} because match callifile!".format(key))
            continue

        # check if matches pattern ---------------------------------------------
        if pattern_to_call is not None:
            if not fnmatch.fnmatch(key, pattern_to_call):
                if verbose:
                    printi("discard {} because match pattern!".format(key))
                continue

        # if come all the way along, call --------------------------------------
        if verbose:
            printi("Call {} !".format(key))
        value()
