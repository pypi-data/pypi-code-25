import sys
from . import roll

try:
    print(", ".join([repr(roll(arg)) for arg in sys.argv[1:]]))
except:
    print('bad input: {}'.format("".join(sys.argv[1:])))