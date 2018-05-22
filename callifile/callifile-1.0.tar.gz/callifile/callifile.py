import inspect
from inspect import getargspec
from printind.printind_function import printi, printiv
import fnmatch


def callifile(module, verbose=False, pattern_to_call=None):
    """Call all the functions in a given module or file. Call only function that
    can be called without arguments or with default arguments.

    - module: the module / file on which call all functions.
    - verbose: True / False (default False)
    - pattern_to_call: call only functions that fit pattern_to_call. Default
        None (call all independantly of pattern matching)"""

    printi("Apply call_all_function_in_this_file on {}".format(module))

    if verbose:
        if pattern_to_call is not None:
            printiv(pattern_to_call)

    all_functions = inspect.getmembers(module, inspect.isfunction)

    for key, value in all_functions:

        if verbose:
            printi("See if should call {}".format(key))

        # check if can be called without argument ------------------------------
        getargspec_output = getargspec(value)
        number_arguments = len(getargspec_output.args)
        if getargspec_output.defaults is None:
            number_arguments = 0
        else:
            number_default_arguments = len(getargspec_output.defaults)

        if (number_arguments > number_default_arguments):
            continue

        # check if it is this function -----------------------------------------
        if (key == "call_all_function_in_this_file"):
            continue

        # check if matches pattern ---------------------------------------------
        if pattern_to_call is not None:
            if not fnmatch.fnmatch(key, pattern_to_call):
                continue

        # if come all the way along, call --------------------------------------
        if verbose:
            printi("Call {}".format(key))
        value()
