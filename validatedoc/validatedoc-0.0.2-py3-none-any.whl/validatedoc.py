#!/usr/bin/env python
"""Validate doc strings, more strictly than pep 257."""
import importlib.util
import inspect
import re
import sys
from types import FunctionType
from types import MethodType
from types import ModuleType
from typing import Any
from typing import Callable
from typing import Dict  # noqa
from typing import Optional
from typing import Tuple


re_match = re.compile(":.*: .*")
re_param = re.compile(":param (?P<name>[a-zA-Z0-9_]*): (?P<text>.*)")
re_return = re.compile(":return: (?P<text>.*)")
re_raises = re.compile(":raises (?P<name>[a-zA-Z0-9_\.]*): (?P<text>.*)")


def get_param(line: str) -> Optional[Tuple[str, str]]:
    """Get whether a line is a param doc string.

    :param line: The line to check
    :return: None if not match, or a tuple of the param name and description
    """
    m = re_param.match(line)
    if m is None:
        return None
    return m.group('name'), m.group('text')


def get_return(line: str) -> Optional[str]:
    """Get whether a line is a return doc string.

    :param line: The line to check
    :return: None if not match, or the return description
    """
    m = re_return.match(line)
    if m is None:
        return None
    return m.group('text')


def get_raises(line: str) -> Optional[Tuple[str, str]]:
    """Get whether a line is a raises doc string.

    :param line: The line to check
    :return: None if not match, or a tuple of the exception and description
    """
    m = re_raises.match(line)
    if m is None:
        return None
    return m.group('name'), m.group('text')


def _print_err(start: str, thing: Any, text: str) -> None:
    """Print an error, starting with ``start``.

    :param start: String to prepend
    :param thing: The thing that caused the error
    :param text: The error message
    """
    info = inspect.getsourcelines(thing)
    if info is None:
        info = ([], 0)
    file = inspect.getsourcefile(thing)

    print(
        "%s: %s:%s:%s - %s" % (start, file, thing.__name__, info[1], text),
        file=sys.stderr,
    )


def print_warning(thing: Any, text: str) -> None:
    """Print a warning.

    :param thing: The thing that caused the error
    :param text: The error message
    """
    _print_err("warning", thing, text)


def print_err(thing: Any, text: str) -> None:
    """Print an error.

    :param thing: The thing that caused the error
    :param text: The error message
    """
    _print_err("error", thing, text)


def validate_function(fun: Callable[..., Any], module: ModuleType) -> bool:
    """Validate a function's docstring.

    :param fun: Function to validate
    :param module: The module to limit checks to
    :return: True if there was an error
    """
    if inspect.getmodule(fun) != module:
        return False

    d = inspect.getdoc(fun)
    if d is None:
        print_err(
            fun,
            "No docstring found",
        )
        return True
    docstring = d.split('\n')

    err = False

    short_desc = docstring.pop(0)
    curr = short_desc
    param_list = []
    ret_exists = False
    raises_list = []

    while docstring:
        last = curr
        curr = docstring[0]

        param = get_param(curr)
        raises = get_raises(curr)
        ret = get_return(curr)
        if param or raises or ret:
            if last:
                print_err(
                    fun,
                    "Must have blank line between description and paramaters",
                )
                err = True
            break
        docstring.pop(0)

    while docstring:
        last = curr
        curr = docstring[0]

        param = get_param(curr)
        raises = get_raises(curr)
        ret = get_return(curr)
        if not (param or raises or ret):
            if not curr:
                # empty line
                print_err(
                    fun,
                    "Found blank line in middle of paramater list",
                )
                continue
            if not curr.startswith('    '):
                print_err(
                    fun,
                    "Found non-indented string in middle of parameter list",
                )
                err = True
        if ret:
            break
        if param is not None:
            param_list.append(param)
        elif raises is not None:
            raises_list.append(raises)

        docstring.pop(0)

    if docstring:
        last = curr
        curr = docstring[0]
        ret = get_return(curr)
        if ret:
            ret_exists = True
        docstring.pop(0)

    for line in docstring:
        if line and not line.startswith('    '):
            print_err(
                fun,
                "Cannot have text after the return documentation",
            )
            err = True

    signature = inspect.signature(fun)
    sig_param_names = set(signature.parameters.keys()) - {'self'}
    param_names = {n for n, _ in param_list}

    undocumented = sig_param_names - param_names
    if undocumented:
        print_err(
            fun,
            "Following parameters don't have docstrings: %s" % undocumented,
        )
        err = True
    extra_doc = param_names - sig_param_names
    if extra_doc:
        print_err(
            fun,
            "Following extra parameters not in function def: %s" % extra_doc,
        )
    ret_ann = signature.return_annotation
    if not (ret_ann is None or ret_ann is signature.empty) and not ret_exists:
        print_err(
            fun,
            "Function return not annotated",
        )
        err = True
    if ret_ann is None and ret_exists:
        print_err(
            fun,
            "Function returns None but return was annotated",
        )
        err = True

    return err


def validate_property(prop: property, module: ModuleType) -> bool:
    """Validate a property.

    :param prop: The property to validate
    :param module: The module to limit checks to
    :return: True if there was an error
    """
    fget = prop.fget
    fset = prop.fset
    fdel = prop.fdel

    err = False

    if fget is None:
        print_warning(
            prop,
            "fget not found for property",
        )

    if fget is not None:
        err = validate_function(fget, module) or err
    if fset is not None:
        err = validate_function(fset, module) or err
    if fdel is not None:
        err = validate_function(fdel, module) or err

    return err


def validate_class(cls: type, module: ModuleType) -> bool:
    """Validate a docstring of the members of a class.

    :param cls: The class to validate
    :param module: The module to limit checks to
    :return: True if there is an error
    """
    if inspect.getmodule(cls) != module:
        return False
    err = False
    for thing in inspect.getmembers(cls):
        try:
            err = validate_thing(thing, module) or err
        except TypeError:
            pass
    return err


def validate_thing(thing: Any, module: ModuleType) -> bool:
    """Validate the docstring on something.

    :param thing: The thing to validate
    :param module: The module to limit the checking to
    :raises TypeError: When thing is not of a type that can be checked
    :return: Whether validation succeeded
    """
    typefuns = {
        FunctionType: validate_function,
        MethodType: validate_function,
        property: validate_property,
        type: validate_class,
        ModuleType: validate_module,
    }  # type: Dict[type, Callable[[Any, ModuleType], bool]]

    fun = typefuns.get(type(thing))
    if fun is None:
        raise TypeError(type(thing))
    return fun(thing, module)


def validate_module(module: ModuleType, _module: ModuleType) -> bool:
    """Validate a module's doc string, and recursively it's classes and funcs.

    :param module: The module to check
    :param _module: For compatibility with the funcion dict in validate_thing
    :return: True if error, false otherwise
    """
    results = []

    members = {
        k: v for k, v in inspect.getmembers(module)
        if hasattr(v, '__module__') and v.__module__ == module.__name__
    }
    for name, member in members.items():
        try:
            results.append(validate_thing(member, module))
        except TypeError as e:
            pass

    return any(results)


def validate(filename: str) -> bool:
    """Validate the module in ``filename``, returning a status code.

    :param filename: The file to open and check
    :return: True if error, false otherwise
    """
    module_name = inspect.getmodulename(filename)
    if module_name is None:
        print(
            "Could not determine module name for %s" % filename,
            file=sys.stderr,
        )
        return True
    spec = importlib.util.spec_from_file_location(module_name, filename)
    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        print("Could not load module for %s" % filename, file=sys.stderr)
        return True
    try:
        loader.exec_module(module)
    except (SystemExit, ImportError):
        # some script SystemExit on import
        # Also just pass if we can't import something
        pass
    sys.modules[module.__name__] = module

    return validate_module(module, module)


def main() -> None:
    """Run the main program."""
    if len(sys.argv) == 1:
        print("Usage: %s file1 file2 ..." % sys.argv[0])
        exit(1)
    files = sys.argv[1:]

    res = [validate(f) for f in files]
    if not any(res):
        exit(0)
    else:
        exit(1)


if __name__ == '__main__':
    main()
