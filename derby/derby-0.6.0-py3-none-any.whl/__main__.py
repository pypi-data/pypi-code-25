import sys
from . import roll

try:
    print(repr(roll(" ".join(sys.argv[1:]))))
except:
    print('bad input: {}'.format("".join(sys.argv[1:])))