def make_instance(cls):
    """
    Transform class in an instance.
    """
    return cls()


@make_instance
class item_getter:  # noqa: N801
    """
    Convert function call to indexing syntax:

    Usage:
        >>> @item_getter
        ... def foo(x):
        ...     return 2 * x
        >>> foo[2]
        4
    """

    def __init__(self, func=None):
        self.func = func or (lambda x: x)

    def __getitem__(self, item):
        return self.func(item)

    def __call__(self, func):
        return type(self)(func)
