from __future__ import absolute_import


def interrupt(func):
    """Decorator for Interrupt function

    Args:
        func (function): Description
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return

    return wrapper
