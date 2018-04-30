import sys
from packone import version

if "-V" in sys.argv[1:]:
    print(version())

