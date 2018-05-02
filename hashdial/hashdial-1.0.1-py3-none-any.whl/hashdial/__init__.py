"""Implements a hash dial for hash based decision making.

Implements, through hashing, decision making that is deterministic on input, but probabilistic across a set of inputs.

For example, suppose a set of components in a distributed system wish to emit a log entry for 1% of requests - but each
component should log the *same* 1% of requests, they could do so as such::

    if hashdial.decide(request.id, 0.01):
        log_request(request)

Seeds
-----

All functions take an optional ``seed`` keyword argument. It is intended to be used in cases where different uses
of the library require orthogonal decision making, or it is desirable to make the decision making unpredictable. In
particular:

* Avoiding untrusted input being tailored to be biased with respect to the hashing algorithm requires use of a seed
  that is not known to the untrusted source.

* Filtering data which is the output of a previous filtering step using the same mechansim, requires use of a different
  seed in order to get correct behavior.

For example, filtering to keep 1% of lines in a file followed by applying the same filter again will result in no
change in output relative to just filtering once - since line that was kept the first time will also be kept the
second time.

Determinism across versions
---------------------------

Any change to an existing function (including default seed and choice of hashing algorithm) that would alter the
output of the function given the same input, will not be done without a major version bump to the library.

API
---
"""
import hashlib
import math
import sys

from typing import TypeVar
from typing import Sequence

DEFAULT_SEED = b''

_MAX_FLOAT_REPRESENTABLE_INT = 2**(sys.float_info.mant_dig) - 1


def _hfloat(b: bytes, seed: bytes) -> float:
    h = hashlib.sha256()
    h.update(seed)
    h.update(b)
    return float(int(h.hexdigest()[0:16], 16)) / 2**64


def decide(key: bytes, probability: float, *, seed: bytes=DEFAULT_SEED) -> bool:
    """
    Decide between ``True`` and `False`` basd on ``key`` such that the probability of ``True`` for a given input
    over a large set of unique inputs is ``probability``.

    For example, to retain 25% of lines read from stdin::

        for line in sys.stdin:
            if decide(line.encode('utf-8'), 0.25):
                sys.stdout.write(line)

    :param key: The bytes to hash.
    :param probability: The probability of a given ``key`` returning True. Must be in range [0, 1].
    :param seed: Seed to hash prior to hashing ``key``.

    :return: Whether to take the action.
    """
    if probability < 0.0:
        raise ValueError('probability must be >= 0.0'.format(probability))
    if probability > 1.0:
        raise ValueError('probability must be <= 1.0'.format(probability))

    return _hfloat(key, seed) < probability


def range(key: bytes, stop: int, *, start: int=0, seed: bytes=DEFAULT_SEED) -> int:
    """
    Select an integer in range ``[start, stop)`` by hashing ``key``.

    Example partitioned filtering of a workload on ``stdin`` assuming this is partition 3 out of 10::

        for line in sys.stdin:
            if range(line.encode('utf-8'), 10) == 3:
                sys.stdout.write(line)

    The difference between stop and start must be sufficiently small to be exactly representable as a
    float (no larger than ``2**(sys.float_info.mant_dig) - 1``).

    :param key: The bytes to hash.
    :param stop: The *exclusive* end of the range of integers among which to select.
    :param start: The *inclusive* start of the range of integers among which to select.
    :param seed: Seed to hash prior to hashing ``key``.

    :return: The selected integer.
    """
    if stop <= start:
        raise ValueError('stop ({}) must be > start ({})'.format(stop, start))

    if stop - start > _MAX_FLOAT_REPRESENTABLE_INT:
        raise ValueError('stop-start must be <= {} due to limitations of floats',
                         _MAX_FLOAT_REPRESENTABLE_INT)

    return int(start + math.floor((stop - start) * _hfloat(key, seed)))


BucketType = TypeVar('BucketType')


def select(key: bytes, seq: Sequence[BucketType], *, seed: bytes=DEFAULT_SEED) -> BucketType:
    """
    Select one of the elements in seq based on the hash of ``key``.

    Example partitioning of input on ``stdin`` into buckets::

        bucketed_lines = {}  # type: Dict[int, str]
        for line in sys.stdin:
            buckets[choice(b, [0, 1, 2, 3, 4, 5])] = line

    :param key: The bytes to hash.
    :param seq: The sequence from which to select an element. Must be non-empty.
    :param seed: Seed to hash prior to hashing b.

    :raise ValueError: If ``seq`` is empty.

    :return: One of the elements in ``seq``.
    """
    if not seq:
        raise ValueError('non-empty sequence required')

    return seq[range(key, len(seq), seed=seed)]
