def interspace(sep, seq):
    """
    Return an iterator that interspace items in seq with the given separator.

    >>> list(interspace(0, [1, 2, 3]))
    [1, 0, 2, 0, 3]
    """
    it = iter(seq)
    try:
        yield next(it)
    except StopIteration:
        pass
    else:
        for item in it:
            yield sep
            yield item
