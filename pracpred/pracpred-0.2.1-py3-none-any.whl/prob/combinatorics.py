"""Combinatorial functions"""
from math import factorial


def permute(n, k):
    """Number of DOSWR of k items from a set of n items."""
    return factorial(n) // factorial(k)


def choose(n, k):
    """Number of DUSWR of k items from a set of n items."""
    return factorial(n) // (factorial(n - k) * factorial(k))


def multichoose(n, k):
    """Number of DOSWR of k items from a set of n items."""
    return choose(n + k - 1, k)


def strings(n, k):
    """Number of DUSWR of k items from a set of n items."""
    return pow(n, k)
