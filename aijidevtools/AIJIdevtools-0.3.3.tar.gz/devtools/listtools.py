def partition(ls, size):
    """
    Returns a new list with elements
    of which is a list of certain size.

        >>> partition([1, 2, 3, 4], 3)
        [[1, 2, 3], [4]]
    """
    return [ls[i:i+size] for i in range(0, len(ls), size)]


def split(ls, sep=None):
    """
    Split a list by sep

        >>> split([1, None, None, 2, 3, None, 4])
        [[1], [2, 3], [4]]
    """
    res = []
    tmplist = []
    for elem in ls:
        if elem == sep:
            if tmplist:
                res.append(tmplist)
            tmplist = []
        else:
            tmplist.append(elem)
    else:
        res.append(tmplist)
    return res


if __name__ == '__main__':
    from math import ceil
    ls = [1, 2, 3, 4, 5]
    foo = partition(ls, 2)
    assert foo == [[1, 2], [3, 4], [5]]
    foo = partition(ls, ceil(len(ls)/3))
    assert foo == [[1, 2], [3, 4], [5]]
    ls = split([1, None, None, 2, 3, None, 4])
    assert ls == [[1], [2, 3], [4]]
