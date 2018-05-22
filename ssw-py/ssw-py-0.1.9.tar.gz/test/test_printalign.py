import sys
try:
    from ssw import (
        SSW,
        force_align,
        print_force_align
    )
except:
    import sys
    from os.path import dirname
    SSW_PATH = dirname(dirname(__file__))
    print(SSW_PATH)
    sys.path.append(SSW_PATH)
    from ssw import (
        SSW,
        force_align,
        print_force_align
    )
LIBNANO_PATH = 'C:\\Users\\Nick\\Documents\\GitHub\\libnano'
sys.path = [LIBNANO_PATH] + sys.path
from libnano.seqstr import (
    reverseComplement,
    complement,
    reverse
)

def align_complement(fwd: str, rev: str):
    rc_rev = reverseComplement(rev)
    alignment = force_align(rc_rev, fwd)
    # print(alignment)
    print_force_align(reverse(rev), fwd, alignment)
# end def

if __name__ == '__main__':
    print("dope")
    align_complement("GGATCCAAA", "TTTGGATC")
    align_complement("GGATCCAAA", "TTGGATC")
    align_complement("GGATCCAAA", "CTTGGATC")


