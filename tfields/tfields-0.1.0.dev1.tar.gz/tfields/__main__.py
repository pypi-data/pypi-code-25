"""
Run doctests on module call
"""
def runDoctests():
    import doctest
    import pathlib
    for f in list(pathlib.Path(__file__).parent.glob('**/*.py')):
        doctest.testfile(f.name)  # , verbose=True, optionflags=doctest.ELLIPSIS)


if __name__ == '__main__':
    runDoctests()
