def read_and_close(filename):
    contents = ''

    with open(filename) as _file:
        contents = _file.read()
    _file.close()

    return contents
