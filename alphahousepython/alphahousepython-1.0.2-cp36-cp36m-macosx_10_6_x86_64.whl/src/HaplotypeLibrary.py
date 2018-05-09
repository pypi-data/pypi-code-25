
import math
from hap import PyHaplotype
import PedigreeHolder
import itertools






class HaplotypeLibraryAlteredException(Exception):
    """Exception to be thrown when there is no genotype information available"""
    def __init__(self):
        Exception.__init__(self, "Haplotype library altered during iteration!")

class HaplotypeLibrary(object):

    def __init__(self, haplotypes = None, individuals = [], coreLengths = None)  -> object:


        self.partialHaplotypes = haplotypes
        if haplotypes is None:
            self.partialHaplotypes = []

        self.fullHaplotypes = []


        for ind in individuals:
            self.fullHaplotypes.append(ind.haplotypes[0])
            self.fullHaplotypes.append(ind.haplotypes[1])

        self.currentIterator = None
        self.workingOnHaplotypes =True
        self.index = 0
        self.coreLengths = coreLengths
        if coreLengths is None:
            coreLengths = []

        self.changed = False

    def __iter__(self):
        self.workingOnHaplotypes = True
        self.index = 0
        self.changed = False
        return self

    def __next__(self):
        if (len(self.partialHaplotypes) ==0 and len(self.fullHaplotypes) == 0): raise StopIteration
        if self.changed: raise HaplotypeLibraryAlteredException
        if self.currentIterator is not None :
            try :
                return self.currentIterator.__next__()
            except StopIteration :
                self.currentIterator = None

        if self.currentIterator is None :

            if self.workingOnHaplotypes :
                if self.index < len(self.partialHaplotypes) :
                    self.index = self.index + 1
                    return self.partialHaplotypes[self.index-1]
                else:
                    self.workingOnHaplotypes = False
                    self.index = 0

            if not self.workingOnHaplotypes :
                if self.index < len(self.fullHaplotypes) :
                    self.currentIterator = haplotypeIterator(self.coreLengths,
                                                             self.fullHaplotypes[self.index]) # Need to actually do the correct thing here.
                    self.index = self.index + 1
                else:
                    raise StopIteration
        return self.__next__()


    def __getitem__(self, item):
        if isinstance(item, list):
            return [self.partialHaplotypes[i] for i in item]
        else:
            try:
                return self.fullHaplotypes[int(item)]
            except ValueError:
                raise TypeError("Wrong type given for getter:" + str(type(item)))


    def __setitem__(self, key, value):

        if (isinstance(value, PedigreeHolder.Individual)):
            # todo check keys
            self.fullHaplotypes.append(value.haplotypes[0])
            self.fullHaplotypes.append(value.haplotypes[1])
        elif (isinstance(value, int)):
            self.coreLengths.append(value)
        elif (isinstance(value, PyHaplotype)):
            self.partialHaplotypes.append(value)

        self.changed = True

    def appendHap(self, h: PyHaplotype):
        self.partialHaplotypes.append(h)

class HaplotypeIterator(object) :

    def __init__(self, coreLengths, offsets, haplotype) :
        self.coreLengths = coreLengths
        self.maxSnp = len(haplotype)
        self.haplotype = haplotype
        self.offsets = offsets

    def __iter__(self):
        for coreLength in self.coreLengths :
            for offset in self.offsets:
                end = 0
                index = 0
                while end < self.maxSnp :
                    end, subHap = self.getHap(coreLength, offset, index)
                    yield ((coreLength, offset, index), subHap)
                    index = index + 1

    def getHap(self, coreLength, offset, index):

        coreLength = min(coreLength, self.maxSnp)
        offset = math.floor(offset*coreLength)
        start = max( index*coreLength - offset, 0)
        end = min( (index + 1)*coreLength  - offset, self.maxSnp)
        return (end, self.haplotype.getSubsetHaplotype(start=start,end=end))


class HaplotypeLibraryFrom(object):
    def __init__(self, individuals=[], coreLengths=[100]):
        self.coreLengths = coreLengths
        self.offsets = [0, .5]
        self.haplotypes = dict()

        for ind in individuals:
            self.add(ind.haplotypes[0])
            self.add(ind.haplotypes[1])

    def add(self, hap):
        hapIter = HaplotypeIterator(self.coreLengths, self.offsets, hap)
        for pair in hapIter:
            index, subHap = pair
            if index not in self.haplotypes :
                self.haplotypes[index] = []
            if subHap.countMissing() == 0:
                try:
                    ii = self.haplotypes[index].index(subHap)
                    self.haplotypes[index][ii].incrementWeight()
                    # print("weight increased", self.haplotypes[index][ii].weight)
                except ValueError:
                    # print("Hap added")
                    self.haplotypes[index].append(subHap)

    def __iter__(self):
        for key, value in self.haplotypes.items():
            for v in value:
                yield v

    def toList(self):
        haps = self.haplotypes.values()

        return list(itertools.chain(*haps))



# class test(object) :
#     def __init__(self, ids) :
#         self.ids = ids
    
#     def __iter__(self) :
#         for idx in self.ids :
#             yield idx

# aa = test([1, 2, 3, 4])
# for idx in aa:
#     print(idx)


























