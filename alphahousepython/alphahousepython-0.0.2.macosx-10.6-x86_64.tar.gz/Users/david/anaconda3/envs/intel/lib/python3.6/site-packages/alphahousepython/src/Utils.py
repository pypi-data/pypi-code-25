import math
from typing import Tuple

from bitstring import BitString

bitMap = {False: BitString('0b0'), True: BitString('0b1')}


def generateParing(xi, yi):
    """Cantor pairing function"""
    if xi < yi:
        x = yi
        y = xi
    else:
        x = xi
        y = yi

    if (x >= y):
        return (x * x + x + y)
    else:
        return (y * y + x)


def unpair(num: int) -> Tuple[int, int]:
    sqrt = math.floor(math.sqrt(float(num)))

    sqrz = sqrt * sqrt

    if ((num - sqrz) >= sqrt):
        x = int(sqrt)
        y = int(num - sqrz - sqrt)

    else:
        x = int(num - sqrz)
        y = int(sqrt)
    # ensures the order does not matter
    if (y > x):
        xout = y
        yout = x
    else:
        xout = x
        yout = y

    return (xout, yout)


def set_bit(v, index, x):
  """Set the index:th bit of v to 1 if x is trur, else to 0, and return the new value."""
  mask = 1 << index   # Compute mask, an integer with just bit 'index' set.
  v &= ~mask          # Clear the bit indicated by the mask (if x is False)
  if x:
    v |= mask         # If x was True, set the bit indicated by the mask.
  return v            # Return the result, we're done.


def countLines(fname):
    """Returns the number of lines in a file"""
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1