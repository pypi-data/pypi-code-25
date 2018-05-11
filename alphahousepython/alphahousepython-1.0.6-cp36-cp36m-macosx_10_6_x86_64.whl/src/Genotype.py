import logging

import numpy as np
from bitarray import bitarray

import Haplotype
import Utils

from Constants import MEMORYSAVE,MISSINGGENOTYPECODE,MISSINGPHASECODE


def checkValid(val):

    if (val == MISSINGGENOTYPECODE or val == 0 or val == 2 or val == 1):
        return True

    return False

class NoGenotypeException(Exception):
    """Exception to be thrown when there is no genotype information available"""
    def __init__(self):
        Exception.__init__(self, "No Genotype Information Present")

class IncorrectHaplotypeNumberError(Exception):
    """Exception thrown when there is an incorrect number of haplotypes given (2 is usually expected)"""
    def __init__(self):
        Exception.__init__(self, "Incorrect number of haplotypes present")


class Genotype(object):
    # !Reminder as to how the data is stored...
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ! Genotype    Homo    Additional !
    # ! 0           1       0          !
    # ! 1           0       0          !
    # ! 2           1       1          !
    # ! Missing     0       1          !

    def __init__(self, array = None,haplotypes  = None, lock= False, length=0):

        # if cython.compiled:
        #     print("Yep, I'm compiled.")
        # else:
        #     print("Just a lowly interpreted script.")
        self.hasLock = False
        self.array = None
        if (not haplotypes is None):
            # first check if we should initialise the genotypes from the haplotypes
            self.__initFromHaplotypes(haplotypes)
        elif (not array is None):
            # otherwise, try to use the array
            if not MEMORYSAVE:
                self.array = np.array(array,dtype=np.int8)
            else:
                self.__initFromArray(array)
        else:
            # otherwise initialise an empty to an array
            missing = np.full(length,fill_value=9,dtype=np.int8)
            if MEMORYSAVE:
                self.__initFromArray(missing)
            else:
                self.array = np.array(missing,dtype=np.int8)

        if (lock):
            self.hasLock = True
            self.locked = bitarray(self.locked)

            for i in range(0,len(self)):
                self.locked[i] = not self.isMissing(i)


    def __initFromArray(self, array):
        self.homo = bitarray(len(array))
        self.additional = bitarray(len(array))

        for i in range(0, len(array)):
            val = int(array[i])
            if (val == 0):
                self.homo[i] = True
                self.additional[i] = False
            elif (val == 1):
                self.homo[i] = False
                self.additional[i] = False

            elif (val == 2):
                self.homo[i] = True
                self.additional[i] = True
            else:  # must be missing
                self.additional[i] = True
                self.homo[i] = False

    def __initFromHaplotypes(self, haplotypes :[Haplotype]) -> 'Genotype':
        """Function populates an array based on what values the haplotypes given have"""
        if (len(haplotypes) != 2):
            raise IncorrectHaplotypeNumberError
        length = min(len(haplotypes[0]), len(haplotypes[1]))

        array = np.full(length,fill_value=9,dtype=np.int8)
        for i,(one,two) in enumerate(zip(haplotypes[0].toIntArray(), haplotypes[1].toIntArray())):

            if ((one == 1) and (two == 1)):
                array[i] = 2
            elif ((one == 0) and (two == 0)):
                array[i] = 0
            elif (one == MISSINGGENOTYPECODE or two == MISSINGGENOTYPECODE):
                # if either is missing - set to missing
                array[i] = MISSINGGENOTYPECODE
            else:
                # if one is 1, and the other is 0
                array[i] = 1
        self.__init__(array)

    def __eq__(self, other : object) -> bool:
        if (isinstance(other,Genotype)):
            if MEMORYSAVE:
                if (self.homo != other.homo or self.additional != other.additional):
                    return False
            else:
                return np.array_equal(self.array, other.array)
        else:
            return False
        return True

    def __len__(self) -> int:

        if MEMORYSAVE:
            return len(self.homo)
        else:
            return len(self.array)

    def __str__(self) -> str:


        if self.array is not None:
            string = " "
            string = string.join(str(x) for x in self.array)
        else:
            string = " "
            string = string.join(str(x) for x in self)
        return  string

    def __getitem__(self, item) :
        if isinstance(item, slice):
            return [self[ii] for ii in range(*item.indices(len(self)))]
        elif isinstance(item, list):
            return [self[ii] for ii in item]
        elif isinstance(item, int):
            if item < 0 or item >= len(self):
                raise IndexError("The index (%d) is out of range." % item)
            else:
                if self.array is not None:
                    return  self.array[item]
                else:
                    return self.getGenotype(item)

    def __setitem__(self, key, value :int):

        if MEMORYSAVE:
            self.setGenotype(key,value)
        else:
            self.setGenotypeArray(key,value)




    def __iter__(self) -> iter:
        self.n = 0

        for i in range(0, len(self)):
            yield (self[i])
        # yield self.getGenotype(self.n)



    def getGenotype(self, pos : int) -> int:
        if not MEMORYSAVE:
            raise NotImplementedError("ERROR - get genotype should only be called in verbose memory mode")
        hom = self.homo[pos]
        add = self.additional[pos]

        if (hom and add):
            return 2
        elif (hom):
            return 0
        elif(add):
            return 9
        else:
            return 1




    def append(self, value : int):
        self[len(self)] = value

    def setGenotypeArray(self, pos, value):
        if not checkValid(value):
            value = MISSINGGENOTYPECODE

        if (pos < len(self)):
            self.array[pos] = value
        if (pos == len(self)):
            self.array = np.append(self.array,[value])
            if (self.hasLock):
                self.locked.append(Utils.bitMap[False])

    def setGenotype(self, pos : int, value : int):
        """sets the value of a genotype at a given position"""

        if not MEMORYSAVE:
            raise NotImplementedError("ERROR - set genotype should only be called in verbose memory mode")
        value = int(value)

        if self.array is not None and pos < len(self.array):
            self.array[pos] = value
        if value == 0:
            hom = True
            add = False
        elif value == 1:
            hom = False
            add = False
        elif value == 2:
            hom= True
            add= True
        else:
            hom = False
            add = True

        if (pos == len(self)):
            self.homo.append(Utils.bitMap[hom])
            self.additional.append(Utils.bitMap[add])

            if (self.hasLock):
                self.locked.append(Utils.bitMap[False])
        else:
            self.homo[pos] = hom
            self.additional[pos] = add

    def toIntArray(self):

        if self.array is not None:
            return self. array
        ret = np.empty(len(self), np.int8)
        c = 0
        for hom,add in zip(self.homo, self.additional):

            if (hom and add):
                ret[c] = 2
            elif (hom):
                ret[c] = 0
            elif (add):
                ret[c] = 9
            else:
                ret[c] = 1
            c+=1

        return ret

    def isHaplotypeCompatable(self, hap: Haplotype, threshold= 0) -> bool:
        """Returns true if number of mismatches are less than threshold"""

        if MEMORYSAVE:
            res = ((self.homo & ~self.additional) & (hap.phase & ~ hap.missing)) \
                  | ((self.homo & self.additional) & (~hap.phase & ~hap.missing))

            x = res.count(True)

        else:
            x = 0
            if (len(self) != len(hap)):
                raise IndexError("Genotype  and Haplotype are different lengths ")
            for i in range(0,len(self)):
                if(self[i] == 0):
                    if not hap[i] == 0 or hap[i] == MISSINGPHASECODE:
                        x += 1
                elif(self[i] == 2):
                   if not hap[i] == 1 or hap[i] == MISSINGPHASECODE:
                       x += 1
        return x <= threshold

    def numHet(self) -> int:
        """Returns the number of Heterozygous snps"""


        if MEMORYSAVE:
            return (~self.homo & ~self.additional).count(True)
        else:
            return (self.array == 1).sum()


    def countMissing(self) -> int:

        if MEMORYSAVE:
            return (~self.homo & self.additional).count(True)
        else:
            return (self.array == 9).sum()



    def percentageMissing(self) -> float:
         return self.countMissing() / len(self)


    def countNotMissing(self):
        return len(self) - self.countMissing()


    def countNotEqual(self, other : 'Genotype') -> int:
        if MEMORYSAVE:
            return ((self.homo ^ other.homo) | (self.additional ^ other.additional)).count(True)
        else:
            return (np.not_equal(self.array, other.array) == True).sum()


    def countNotEqualExcludeMissing(self, other : 'Genotype') -> int:

        if MEMORYSAVE:
            return (((self.homo ^ other.homo) | (self.additional ^ other.additional)) & ((self.homo | ~self.additional) & (other.homo | ~other.additional))).count(True)
        else:
            count = 0
            for i in range(0, len(self)):
                if not (self[i] == MISSINGGENOTYPECODE or other[i] == MISSINGGENOTYPECODE):
                    if (self[i] != other[i]):
                        count+=1
            return count

    def countMismatches(self, other: 'Genotype') -> int:
        """Counts the number of opposing homozygotes between the two genotypes
             Parameters
        ------------
        other : Genotype
            Genotype to be compared with


        """
        if MEMORYSAVE:
            x = ((self.homo & other.homo) & (self.additional ^ other.additional))
            return x.count(True)
        else:
            count = 0
            for i in range(0, len(self)):
                if self[i] == 0:
                    if other[i] == 2:
                        count += 1
                elif self[i] == 2:
                    if other[i] == 0:
                        count += 1
            return  count

    def isMissing(self, pos):
        if self[pos] == MISSINGGENOTYPECODE:
            return True
        return False

    def getSubsetGenotype(self, startPos = 0, endPos = 0):
        """Returns a subset genotype object
                     Parameters
                ------------
                startPos : int
                    starting position of new genotype
                endPos : int
                |   end position


                """
        if (endPos == 0):
            endPos = len(self) - 1
        if (endPos > len(self) - 1):
            logging.exception("WARNING subset given size too big as end position")
            endPos = len(self) - 1

        if MEMORYSAVE:
            empty = np.full((endPos - startPos), MISSINGGENOTYPECODE)
            g = Genotype(empty)

            g.homo = self.homo[startPos:endPos]
            g.additional = self.additional[startPos:endPos]
        else:
            g = Genotype(self.array[startPos:endPos])
        return g


    def complement(self,h:Haplotype) -> Haplotype:


        if (len(self) != len(h)):
            raise IndexError("Genotype and Haploype are different lengths ")
        if MEMORYSAVE:
            phase = bitarray(len(self))
            missing = bitarray(len(self))

            y =(h.phase & ~h.missing)
            x = ((y & self.homo))

            phase = ((h.phase & h.missing) | (((h.phase & ~h.missing) & self.homo) | (~(h.phase | h.missing) & ~(self.homo ^ self.additional))))

            missing = (h.missing | (self.additional & ~self.homo)|  ((~h.phase & self.additional) & h.phase & (self.homo ^ self.additional )))

            return Haplotype.Haplotype(phase=phase, missing= missing)

        else:
            array = np.full(len(self), MISSINGPHASECODE)


            for i in range(0, len(self)):

                if (self[i] == 0):
                    array[i] = 0
                elif (self[i] == 2):
                    array[i] = 1
                elif (self[i] == 1):

                    if (h[i] ==1):
                        array[i] = 0
                    elif (h[i] == 0):
                        array[i] = 1

            return Haplotype.Haplotype(array)




    def setFromHaplotypesIfMissing(self, h1: Haplotype,h2: Haplotype):

        tempG = Genotype(haplotypes=(h1,h2))

        self.setFromOtherIfMissing(tempG)

    def setFromOtherIfMissing(self,other : 'Genotype'):

        if (len(self) != len(other)):
            raise IndexError("Genotype are different lengths ")
        if MEMORYSAVE:
            origHom = self.homo

            self.homo = (((self.homo | ~self.additional) & self.homo)  | ((~self.homo & self.additional) & other.homo))
            self.additional = ((( origHom | ~self.additional) & self.additional) | ( ( ~origHom & self.additional) & other.additional ))
        else:
            for i in range(0, len(self)):
                if  self[i] == 9:
                    self[i] = other[i]
