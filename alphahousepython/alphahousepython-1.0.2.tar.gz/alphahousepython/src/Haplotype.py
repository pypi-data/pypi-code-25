# cython: linetrace=True
# cython: binding=True


from typing import Union, List

import numpy as np
from bitarray import bitarray
# from Genotype import  Genotype
# import Genotype
import Genotype as Genotype
import Utils as Utils

use_numba = True
try:
    import numba as nb
    from nb import jit, int8, int32, boolean, jitclass
except ImportError:
    use_numba = False
    from _faker import jit, int8, int32, boolean, jitclass

from Constants import MEMORYSAVE, ERRORPHASECODE, MISSINGPHASECODE


class EmptyHaploypeException(Exception):
    def __init__(self):
        Exception.__init__(self, "Empty Haplotype given")


def checkValid(val):
    if (val == MISSINGPHASECODE or val == 0 or val == 1):
        return True

    return False


if (use_numba):
    spec = [
        ('array', int8[:]),  # a simple scalar field
        ('phase', int8[:]),  # an array field
        ('missing', int8[:]),
        ('lock', boolean[:]),
        ('start', int32),
        ('weight', int32),
        ('boolean', boolean)
    ]


# @jitclass(spec)
class Haplotype:
    """
     Phase       Phase   Missing !
     0           0       0       !
     1           1       0       !
     Missing     0       1       !
     Error       1       1       !
    """

    def __init__(self, array=None, phase=None, missing=None, locked=None, lock=False, start=0, weight=1):
        """
        Default constructor for haplotypes

        Takes in array (that can be converted to ints) and assigns haplotype object


        Parameters
        ------------
        array : [int]
            array of 0,1,9 of haplotype information
        lock : [bool]
            And an iterable boolean of items that should be locked


        """

        if array is None:
            array = []
        if (len(array) > 0):

            if MEMORYSAVE:
                self.__initFromArray(array, lock)
            else:
                self.array = np.array(array, dtype=np.int8)
        elif (phase != None and missing != None):
            self.__initFromBitArrays(phase, missing, locked)
        else:

            self.locked = []
            if MEMORYSAVE:
                self.missing = []
                self.phase = []
            else:
                self.array = []

        self.start = start
        self.weight = weight
        self.hasLock = False  # this is a boolean

    def getEnd(self) -> int:
        return len(self) + self.start

    def __initFromBitArrays(self, phase: bitarray, missing: bitarray, locked: bitarray):
        self.phase = phase
        self.missing = missing
        self.locked = locked

    def __initFromArray(self, array, lock):
        self.phase = bitarray(len(array))
        self.missing = bitarray(len(array))
        self.locked = bitarray(len(array))


        for i in range(0, len(self)):
            val = int(array[i])
            if (val == 1):
                self.phase[i] = True
                self.missing[i] = False
            elif (val == 0):
                self.phase[i] = False
                self.missing[i] = False
                # everything is already 0
            elif (val == MISSINGPHASECODE):
                self.phase[i] = False
                self.missing[i] = True
            else:  # set to erro
                # TODO throw error
                self.phase[i] = True
                self.missing[i] = True

        if (lock):
            self.hasLock = True
            self.locked = bitarray(len(self))

            for i in range(0, len(self)):
                self.locked[i] = (~ self.missing[i])

    def __len__(self) -> int:
        """returns length of haplotype"""

        if MEMORYSAVE:
            return len(self.phase)
        else:
            return len(self.array)

    def __getitem__(self, item) -> Union[int, List[int]]:
        """gets haplotype at given snp"""
        if isinstance(item, slice):
            return [self[ii] for ii in range(*item.indices(len(self)))]
            # TODO think
            # return self.getSubsetHaplotype(start=item.start,end=item.stop)
        elif isinstance(item, list):
            return [self[ii] for ii in item]
        elif isinstance(item, int):
            if item < 0 or item >= len(self):
                raise IndexError("The index (%d) is out of range." % item)
            else:
                if MEMORYSAVE:
                    return self.getPhase(item)
                else:
                    return self.array[item]

    def getSubsetHaplotype(self, start: int, end: int) -> 'Haplotype':
        """ Start of subset haplotype is current haplotype start + start"""

        start = int(start)
        end = int(end)
        return Haplotype(self[start:end], start=start + self.start, weight=self.weight)

    def __eq__(self, other: object) -> bool:
        """compares two haplotpyes"""
        if isinstance(other, Haplotype):
            if self.start != other.start:
                return False

            if MEMORYSAVE:
                if self.phase != other.phase or self.missing != other.missing:
                    return False
            else:
                return np.array_equal(self.array, other.array)

        else:
            return False
        return True
    def contains(self, index) :
        return index >= self.start and index < self.getEnd()

    def toIntArray(self) -> np.ndarray:
        """Returns an integer (int8) array of the haplotype.
                """

        if not MEMORYSAVE:
            return self.array

        ret = np.empty(len(self), np.int8)
        c = 0
        for hom, add in zip(self.phase, self.missing):

            if (hom and add):
                ret[c] = 9
            elif (hom):
                ret[c] = 1
            elif (add):
                ret[c] = 9
            else:
                ret[c] = 0
            c += 1

        return ret

    # Some utility functions to make haplotype math/comparisons moderately easier. This may be a bad idea. Not using (or tested) for now.
    def toZeroOneIntArray(self) -> np.ndarray:
        """Returns an integer (int8) array of the haplotype.
                """

        ret = np.zeros(len(self), np.int64)
        if not MEMORYSAVE:
            np.place(ret, self.array == MISSINGPHASECODE, 0)
            np.place(ret, self.array == 1, 1)
            return ret
        c = 0
        for hom, add in zip(self.phase, self.missing):

            if (hom and add):
                ret[c] = 0
            elif (hom):
                ret[c] = 1
            elif (add):
                ret[c] = 0
            else:
                ret[c] = 0
            c += 1

        return ret

    def toNonMissingArray(self) -> np.ndarray:
        """Returns an integer (int8) array of the haplotype.
                """
        ret = np.zeros(len(self), np.int64)
        if not MEMORYSAVE:
            np.place(ret, self.array == MISSINGPHASECODE, 0)
            np.place(ret, self.array != MISSINGPHASECODE, 1)
            return ret

        c = 0
        for hom, add in zip(self.phase, self.missing):

            if (hom and add):
                ret[c] = 0
            elif (hom):
                ret[c] = 1
            elif (add):
                ret[c] = 0
            else:
                ret[c] = 1
            c += 1

        return ret

    def __setitem__(self, key: int, value: int):

        if MEMORYSAVE:
            self.setPhase(key, value)
        else:
            self.setPhaseArray(key, value)

    def __iter__(self):
        for i in range(0, len(self)):
            if MEMORYSAVE:
                yield self.getPhase(i)
            else:
                yield self.getPhaseArray(i)

    def getPhase(self, pos: int):
        if not MEMORYSAVE:
            raise NotImplementedError("ERROR - get phase should only be called in verbose memory mode")
        if (self.missing[pos] and self.phase[pos]):
            return ERRORPHASECODE
        elif (self.missing[pos]):
            return MISSINGPHASECODE
        elif (self.phase[pos]):
            return 1
        else:
            return 0

    def getPhaseArray(self, pos : int):
        return self.array[pos]

    def append(self, value: int):
        self[len(self)] = value

    def setPhaseArray(self, pos, value):
        if not checkValid(value):
            value = MISSINGPHASECODE

        if (pos < len(self)):
            self.array[pos] = value
        if (pos == len(self)):
            self.array = np.append(self.array, [value])
            if (self.hasLock):
                self.locked.append(Utils.bitMap[False])

    def setPhase(self, pos: int, value: int):

        value = int(value)
        if (value == 0):
            phase = False
            miss = False
        elif (value == 1):
            phase = True
            miss = False
        elif (value == MISSINGPHASECODE):
            phase = False
            miss = True
        else:
            phase = True
            miss = True

        if (pos == len(self)):
            self.phase.append(Utils.bitMap[phase])
            self.missing.append(Utils.bitMap[miss])

            if (self.hasLock):
                self.locked.append(Utils.bitMap[False])
        else:
            self.phase[pos] = phase
            self.missing[pos] = miss

    def __str__(self):

        if self.array is not None:
            string = " "
            string = string.join(str(x) for x in self.array)
        else:
            string = ""
            for i in range(0, len(self)):
                string += str(self.getPhase(i)) + " "
        return string

    def setFromOtherIfMissing(self, oh: 'Haplotype'):
        '''!> @brief   Sets one haplotypes from another if the first is missing
        !> @detail  Uses the following rules per snp:
        !>        1) If haplotype 1 is phased then return that phase
        !>        2) If haplotype 1 is missing but haplotype 2 is phased then
        !>          return that phase
        !>        3) If both are unphased and both error then error
        !>        4) If both are missing then missing
        !> @date    May 25, 2017'''

        if (len(self) != len(oh)):
            raise IndexError("Haplotypes are different lengths ")

        if MEMORYSAVE:
            self.phase = ((~self.missing & self.phase) | (self.missing & oh.phase))
            self.missing = (self.missing & oh.missing)
        else:
            for i in range(0, len(self)):
                if self[i] == MISSINGPHASECODE:
                    if (oh[i] == 1):
                        self[i] = 1
                    elif (oh[i] == 0):
                        self[i] = 0

    def setFromGenotypeIfMissing(self, g: Genotype):
        if (len(self) != len(g)):
            raise IndexError("Genotype  and Haplotype are different lengths ")

        if MEMORYSAVE:
            self.phase = ((~self.missing & self.phase) | (self.missing & (g.homo & g.additional)))
            self.missing = ~g.homo & self.missing
        else:
            for i in range(0, len(self)):
                if self[i] == MISSINGPHASECODE:

                    if (g[i] == 2):
                        self[i] = 1
                    elif (g[i] == 0):
                        self[i] = 0

    def countMissing(self) -> int:
        if MEMORYSAVE:
            return (~self.phase & self.missing).count(True)
        else:
            return (self.array == 9).sum()

    def countNotMissing(self) -> int:

        return len(self) - self.countMissing()

    def countNotEqualExcludeMissing(self, other):
        if MEMORYSAVE:
            return (((self.phase ^ other.phase) | (self.missing ^ other.missing)) & (
                        (~self.missing) & (~other.missing))).count(True)
        else:
            count = 0
            for i in range(0, len(self)):
                if not (self[i] == MISSINGPHASECODE or other[i] == MISSINGPHASECODE):
                    if (self[i] != other[i]):
                        count += 1
            return count

    def percentageMissing(self) -> float:
        return self.countMissing() / len(self)


class IntersectCompare:

    def __init__(self, matching, nonMatching, nonMissing, total):
        self.matching = matching
        self.nonMatching = nonMatching
        self.nonMissing = nonMissing
        self.total = total


# if (use_numba):
@jit(parallel=True)
def compareHapsOnIntersect(hap1: Haplotype, hap2: Haplotype) -> IntersectCompare:
    if not MEMORYSAVE:
        return compareHapsOnIntersectArray(hap1, hap2)
    nonMissing = 0
    matching = 0

    start = max(hap1.start, hap2.start)
    end = min(len(hap1) + hap1.start, len(hap2) + hap2.start)

    h1 = hap1.getSubsetHaplotype(start - hap1.start, end - hap1.start)
    h2 = hap2.getSubsetHaplotype(start - hap2.start, end - hap2.start)
    if h1.length == 0 or h2.length == 0:
        return IntersectCompare(0, 0, 0, end - start + 1)

    nonMissing = (~h1.missing & ~h2.missing).count(True)

    matching = ((~h1.missing & ~h2.missing) & ((h1.phase & h2.phase) ^ ((~h1.phase & ~h2.phase)))).count(True)

    nonMatching = nonMissing - matching
    return IntersectCompare(matching, nonMatching, nonMissing, end - start + 1)


def compareHapsOnIntersectArray(hap1: Haplotype, hap2: Haplotype) -> IntersectCompare:
    if MEMORYSAVE:
        return compareHapsOnIntersect(hap1, hap2)
    nonMissing = 0
    matching = 0
    missing = 9

    if (len(hap1.array) == 0):
        hap1.array = hap1.toIntArray()
    if (len(hap2.array) == 0):
        hap2.array = hap2.toIntArray()

    hap1Start = hap1.start
    hap2Start = hap2.start
    hap1Array = hap1.array
    hap2Array = hap2.array

    hap1Length = len(hap1)
    hap2Length = len(hap2)

    start = max(hap1Start, hap2Start)
    end = min(hap1Length + hap1Start, hap2Length + hap2Start)
    for i in range(start, end):
        ind1 = i - hap1Start
        ind2 = i - hap2Start
        if (hap1Array[ind1] != missing and hap2Array[ind2] != missing):
            nonMissing += 1

            if (hap1Array[ind1] == hap2Array[ind2]):
                matching += 1

    nonMatching = nonMissing - matching
    return IntersectCompare(matching, nonMatching, nonMissing, end - start + 1)


