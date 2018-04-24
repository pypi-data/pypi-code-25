__author__ = 'H.D. "Chip" McCullough IV'

def dict_diff(expected: dict, actual: dict) -> dict:
    """

    :param expected:
    :param actual:
    :return:
    """

    diff = {}

    for key in actual.keys():
        if expected.get(key) is not actual.get(key):
            diff.update({key: actual.get(key)})

    return diff