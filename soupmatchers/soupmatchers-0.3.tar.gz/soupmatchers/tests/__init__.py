from __future__ import print_function


def load_tests(loader, standard_tests, pattern):
    import doctest
    import os
    import sys

    this_dir = os.path.dirname(__file__)
    standard_tests.addTests(
        loader.discover(start_dir=this_dir, pattern=pattern))
    source_readme_path = os.path.join(
        os.path.dirname(os.path.dirname(this_dir)), "README")
    if os.path.exists(source_readme_path):
        standard_tests.addTest(
            doctest.DocFileTest(os.path.relpath(source_readme_path, this_dir),
                optionflags=doctest.NORMALIZE_WHITESPACE,
                globs={'print_function': print_function}))
    else:
        sys.stderr.write("Warning: not testing README as it can't be found")
    return standard_tests

