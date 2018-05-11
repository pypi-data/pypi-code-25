# -*- coding: utf-8 -*-
# cython: linetrace=True
# cython: binding=True

"""PedigreeHolder.py

Module containing all of the invdividual logic of dealing with pedigree information

Attributes:

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

"""

import csv
import re
import typing
from collections import OrderedDict
from enum import Enum
from typing import *
from gen import PyGenotype
from hap import PyHaplotype, compareHapsOnIntersectArray
import numpy as np
import pandas as pd



try:
    from plinkio import plinkfile
except ImportError:
    use_plink = False

import Utils as Utils
# from Genotype import Genotype,NoGenotypeException
# from Haplotype import Haplotype, compareHapsOnIntersect,compareHapsOnIntersectArray

from bitarray import bitarray
import HaplotypeLibrary as HaplotypeLibrary
from Constants import MEMORYSAVE,MISSINGGENOTYPECODE,MISSINGPHASECODE
NOPARENT = '0'
try:
    import numba as nb
    from nb import jit, int8, int32, boolean, jitclass
except ImportError:
    use_numba = False
    from _faker import jit, int8, int32, boolean, jitclass

# "ctypedef" assigns a corresponding compile-time type to DTYPE_t. For
# every type in the numpy module there's a corresponding compile-time
# type with a _t-suffix.



#####THIS SHOULD NOT BE HERE!!! (but I'm sticking it here anyways...)




class Gender(Enum):
    """SIMPLE ENUM CLASS SHOWING GENDER"""
    MALE = 1
    FEMALE = 2
    UNKNOWN = 9


class Inconsistencies:
    """Class for representing mendelian inconsistencies, in terms of parental inconsistencies"""

    def __init__(self, g, pg, mg):

        if MEMORYSAVE:
            het = (~ (g.homo | g.additional)) & ((pg.homo & mg.homo) & (~pg.additional ^ mg.additional))

            self.maternalInconsistent = (het | ((g.homo & mg.homo) & (g.additional ^ mg.additional)))
            self.paternalInconsistent = (het | ((g.homo & pg.homo) & (g.additional ^ pg.additional)))


            patPres = pg.homo | ~pg.additional
            matPres = mg.homo | ~mg.additional
            indPres = g.homo | ~g.additional


        else:
            self.maternalInconsistent = bitarray(len(g))
            self.paternalInconsistent = bitarray(len(g))
            patPres = bitarray(len(g))
            matPres = bitarray(len(g))
            indPres = bitarray(len(g))
            for i in range(0, len(g)):
                if (g[i] != MISSINGGENOTYPECODE):
                    indPres[i] = True
                else:
                    indPres[i] = False
                if (pg[i] != MISSINGGENOTYPECODE):
                    patPres[i] = True
                else:
                    patPres[i] = True
                if (mg[i] != MISSINGGENOTYPECODE):
                    matPres[i] = True
                else:
                    matPres[i] = True

                # corresponds to HET step above
                if (g[i] == 1 and ((pg[i] == 0 and mg[i] == 2) or (pg[i]==2 and mg[i] == 0 ))):
                    self.maternalInconsistent[i] = True
                    self.paternalInconsistent[i] = True
                    continue

                if (g[i] == 0 and pg[i] == 2) or (g[i] == 2 and pg[i] == 0):
                    self.paternalInconsistent[i] = True

                if (g[i] == 0 and mg[i] == 2) or (g[i] == 2 and mg[i] == 0):
                    self.maternalInconsistent[i] = True

        self.individualInconsistent = self.paternalInconsistent | self.maternalInconsistent

        self.paternalConsistent = (indPres & patPres) & (~ self.paternalInconsistent)
        self.maternalConsistent = (indPres & matPres) & (~self.maternalInconsistent)
        self.individualConsistent = (indPres & matPres & patPres) & ~self.individualInconsistent





class Individual:

    def __init__(self, id, sireId, damId, founder, recId, gender = Gender.UNKNOWN,
                 genotype = None,
                 haplotypes = None, initToSnps= 0):
        """Default constructor of Individual"""
        self.id  = id
        self.recId  = recId
        self.sireId  = sireId
        self.damId  = damId
        self.offsprings  = []
        self.sire  = None
        self.dam = None
        self.founder = founder
        self.generation = 0
        self.genotype = genotype
        self.haplotypes = haplotypes
        self.inconsistenciesCount = 0
        self.inconsistencies = None
        self.mend = None
        self.reads = []
        self.gender = gender

        self.weight = 0
        if (self.haplotypes is None):
            self.haplotypes = []

        if (initToSnps != 0):
            missingArray = np.full(initToSnps, 9)
            if (self.haplotypes is None):
                self.haplotypes[0] = PyHaplotype(missingArray)
                self.haplotypes[1] = PyHaplotype(missingArray)
            else:

                for i in range(len(self.haplotypes[0]), initToSnps):
                    self.haplotypes[0][i] = 9  # extends haplotype object
                    self.haplotypes[1][i] = 9  # extends haplotype object

            if (self.genotype is None):
                self.genotype = PyGenotype(missingArray)
            else:
                for i in range(len(self.genotype), initToSnps):
                    self.genotype[i] = 9

    def getInconsistencies(self) -> Optional[Inconsistencies]:

        if (self.genotype is None):
            pass
        self.inconsistencies = np.zeros(len(self.genotype))
        if (not (self.sire is None or self.dam is None)):
            self.mend = Inconsistencies(self.genotype, self.sire.genotype, self.dam.genotype)
            return self.mend
        return None




    def getParentBasedOnIndex(self, index) -> 'Individual':

        if (index == 0):
            return self.sire
        elif (index == 1):
            return self.dam

    def indivParentHomozygoticFillIn(self, hetGameticStatus=None, homGameticParent=0):

        if not self.founder:
            #

            for e in range(0, 2):
                parent = self.getParentBasedOnIndex(e)

                tmpG = PyGenotype(haplotypes=parent.haplotypes)
                self.haplotypes[e].setFromGenotypeIfMissing(tmpG)
            self.makeIndividualGenotypeFromPhase()

    def __hash__(self):
        """Returns the hash of the id"""
        return self.id.__hash__()

    # def __dict__(self) -> dict:
    #
    #     ret = {}
    #     ret["id"] = self.id
    #     ret["recI"] = self.recId
    #     ret["sireId"] = self.sireId
    #     ret["damId"] = self.damId
    #     ret["nOffs"] = len(self.offsprings)
    #     #do all offsprings
    # #     currently doesn't do genotypes and haplotypes

    def __eq__(self, o: object) -> bool:

        if (not isinstance(o, Individual)):
            return False

        if (not self.id == o.id):
            return False

        if (not self.recId == o.recId):
            return False

        if (not self.sireId == o.sireId):
            return False

        if (not self.damId == o.damId):
            return False
        return True

    def getParentArray(self) -> []:

        return (self.sire, self.dam)

    def __str__(self) -> str:
        return self.id + " " + self.sireId + " " + self.damId + '\n'

    def addOffspring(self, offspring: 'Individual'):

        self.offsprings.append(offspring)
        if (offspring.sireId == self.id):
            offspring.sire = self
            self.gender = Gender.MALE
        elif (offspring.damId == self.id):
            offspring.dam = self
            self.gender = Gender.FEMALE
        else:
            print("ERROR - animal is being given offspring that is unrelated")

    def writeOutPhase(self) -> str:
        '''Prints out the phase in alphasuite format
            This is a two line per individual format
            e.g.
            ANIMID 1 0 0 1
            ANIMID 1 0 1 0
        '''
        string = ""
        if (len(self.haplotypes) != 0):
            string += self.id + " " + str(self.haplotypes[0]) + '\n'
            string += self.id + " " + str(self.haplotypes[1]) + '\n'
        else:
            string += self.id + '\n'
            string += self.id + '\n'

        return string

    def writeOutGenotypes(self) -> str:
        """returnsthe genotype information as a string per individual
            If no genotype is present, tries to create genotype information if haplotypes are present"""

        string = ""

        if (len(self.haplotypes) == 0 and self.genotype == None):
            return self.id + '\n'

        elif (self.genotype == None):
            self.genotype = np.full(1, fill_value=9, dtype=np.int8)
            # self.genotype = PyGenotype(haplotypes=self.haplotypes)

        string += self.id + " " + str(self.genotype) + '\n'

        return string

    def removeOffspring(self, offspring: 'Individual', dummy=None):
        """Removes offspring object, and fixes pointer fields in offspring"""
        self.offsprings.remove(offspring)

        if (offspring.sireId == self.id):
            offspring.sire = dummy

            if (dummy is not None):
                offspring.sireId = dummy.id
            else:
                offspring.sireId = '0'
        elif (offspring.damId == self.id):
            offspring.dam = dummy
            if (dummy is not None):
                offspring.damId = dummy.id
            else:
                offspring.damId = '0'
        else:
            print("ERROR - animal is being given offspring that is unrelated")


    def makeIndividualPhaseCompliment(self):

        comp2 = self.genotype.complement(self.haplotypes[0])
        comp1 = self.genotype.complement(self.haplotypes[1])

        self.haplotypes[0].setFromOtherIfMissing(comp1)
        self.haplotypes[1].setFromOtherIfMissing(comp2)

    def makeIndividualGenotypeFromPhase(self):
        if self.genotype is None:
            self.genotype = PyGenotype(length=len(self.haplotypes[0]))
        self.genotype.setFromHaplotypesIfMissing(self.haplotypes[0], self.haplotypes[1])
    @jit
    def indivHomoFillIn(self):

        for i, val in enumerate(self.genotype):
            if (val == 2):
                self.haplotypes[0][i] = 1
                self.haplotypes[1][i] = 1
            if (val == 0):
                self.haplotypes[0][i] = 0
                self.haplotypes[1][i] = 0

    def getPercentageNonMissingHaps(self) -> tuple:
        return (1 - self.haplotypes[0].percentageMissing(),1 - self.haplotypes[1].percentageMissing())

    def isFullyPhased(self) -> bool:
        hap1, hap2 = self.getPercentageNonMissingHaps()
        return hap1 + hap2 == 2

    def isHD(self, HDTHRESHOLD = 0.9) -> bool:
        return self.getPercentageNonMissingGeno() > HDTHRESHOLD

    def getPercentageNonMissingGeno(self) -> float:
        return 1 - self.genotype.percentageMissing()

    def randomlyPhasedMidPoint(self):


        if self.genotype is None: raise NoGenotypeException
        mid = len(self.genotype) /2

        index = -1
        for i in range(0, len(self.genotype)-int(mid)-1):

            if self.genotype[int(mid) + i] == 1:
                index = int(mid) + i
                break
            if self.genotype[int(mid) - i] == 1:
                index = int(mid) - i
                break
        if index != -1 :
            self.haplotypes[0][index] = 0
            self.haplotypes[1][index] = 1
        
        areDifferent = compareHapsOnIntersectArray(self.haplotypes[1], self.haplotypes[0])
        # print("Post Phasing", areDifferent.matching, areDifferent.nonMatching)

        # if index == -1: 
        #     print("No midpoint found")


class DummyIndiv(Individual):
    """Individual that is defined as a DUMMY"""

    def __init__(self):
        super(DummyIndiv, self).__init__('0', '0', '0', True, 0)


class Pedigree:
    """Pedigree

    Class contains individual objects, as well as ordered dictionary of genotyped individuals

    Also contains founders (which is also an ordered dictionary)



    """

    def __init__(self, file= None, plinkFile= None, array = None,
                 genotypeArray = None, initToSnps= 0):
        self.individuals = OrderedDict()

        self.genotypedIndividuals = OrderedDict()
        self.founders = OrderedDict()
        self.generations = []
        self.sorted = False

        if plinkFile is not None:
            self.__initFromPlinkFile(plinkFile)


        elif file is not None:
            self.__initFromFile(file, genotypeArray, initToSnps)

        elif array is not None:
            self.__initFromArray(array, genotypeArray, initToSnps)

    def __initFromFile(self, file, genotypes=None, initToSnps=0):
        i = open(file, 'r')
        array = []  # should be array of string tuple

        # add 0 in to state that pedigree is ordered

        for l in i:
            s = l.rstrip().split(" ")
            s = list(filter(lambda name: name.strip(), s))
            array.append(s)

        i.close()
        self.__initFromArray(array, genotypes, initToSnps)

    def __initFromArray(self, animal_array, genotypes= None, initToSnps=0):
        """Inits pedigree from array"""
        zero = DummyIndiv()

        self['0'] = zero
        count = 0

        animals = []  # list should be a tuple
        temp = []

        gCount = 0

        for s in animal_array:
            Founder = False
            if (s[1] == NOPARENT and s[2] == NOPARENT):
                Founder = True
            g = None
            if (genotypes is not None):
                g = PyGenotype(genotypes[gCount])
                gCount += 1
            elif initToSnps != 0:  # if in
                g = PyGenotype(np.full(initToSnps, 9))
            animal = Individual(s[0], s[1], s[2], Founder, count, g)

            if (g is not None):
                self.genotypedIndividuals[s[0]] = animal

            if Founder:
                self.founders[animal.id] = animal

            elif (animal.sireId in self.individuals and animal.damId in self.individuals):
                animals.append(animal)
                self[animal.sireId].addOffspring(animal)
                self[animal.damId].addOffspring(animal)
            else:
                temp.append(animal)
            self[s[0]] = animal  # actually a anim to ped

        for e in temp:
            if (e.sireId in self.individuals):
                self[e.sireId].addOffspring(e)
            elif (e.sireId != NOPARENT):
                self[e.sireId] = Individual(e.sireId, NOPARENT, NOPARENT, True, len(self) + 1)
                self[e.sireId].addOffspring(e)
            else:
                print(("ERROR in ped - contact developer"))

            if (e.damId in self.individuals):
                self[e.damId].addOffspring(e)
            elif (e.damId != NOPARENT):
                self[e.damId] = Individual(e.damId, NOPARENT, NOPARENT, True, len(self) + 1)
                self[e.damId].addOffspring(e)

                # e.damId = '0'
                # e.founder = True
                # self.founders.append(e)

    def __initFromPlinkFile(self, fileName: str, startSnp= None, endSnp= None):
        pf = plinkfile.open(fileName)

        samples = pf.get_samples()
        locus = pf.get_loci()

        nSnp = len(locus)
        nInd = len(samples)
        if (startSnp is None):
            startSnp = 0
        if (endSnp is None):
            endSnp = nSnp

        array = []
        for ind in samples:
            a = [ind.iid, ind.father_iid, ind.mother_iid]
            array.append(a)

        values = np.zeros((nInd, endSnp - startSnp))

        for snpIndex in range(startSnp - 1):
            pf.next()
        for snpIndex in range(endSnp - startSnp):
            if snpIndex % 1000 == 0: print("read %s out of %s" % (snpIndex, endSnp - startSnp + 1))
            row = np.array(pf.next())
            maf = np.mean(row)
            values[:, snpIndex] = np.array(row) - maf  # Maf Centered

        self.__initFromArray(animal_array=array, genotypes=values)

    def __str__(self) -> str:
        arr = ([str(item) for item in list(self.individuals.values())])
        return ''.join(arr)

    def getPhaseAsString(self) -> str:
        """gets phase information for all non dummy animals as a string"""
        arr = (
        [item.writeOutPhase() for item in list(self.individuals.values()) if (not (isinstance(item, DummyIndiv)))])
        return ''.join(arr)

    def writeOutPhase(self, file):
        """Writes out phase information to file"""
        f = open(file, 'w')

        for i in self:
            if (isinstance(i, DummyIndiv)): continue
            f.write(i.writeOutPhase())
        f.close()

    def getGenotypesAsString(self) -> str:
        arr = (
        [item.writeOutGenotypes() for item in list(self.individuals.values()) if (not (isinstance(item, DummyIndiv)))])
        return ''.join(arr)

    def writeOutGenotypes(self, file):
        "writes out genotype informations to a file"
        f = open(file, 'w')

        for i in self:
            if (isinstance(i, DummyIndiv)): continue
            f.write(i.writeOutGenotypes())
        f.close()

    def getGenotypesAll(self) -> np.ndarray:
        """Function returns all genotypes in an array

        :return np.ndarray[indviduals, snps]
        """
        ret = np.zeros((len(self.individuals), len(self[0].genotype)))

        for ind in self.individuals:
            np.append(ret, ind.genotype.toIntArray())
        return ret

    def getGenotypes(self) -> np.ndarray:
        """Gets 3D array of genotypes"""

        ret = np.zeros((len(self.genotypedIndividuals), len(self.genotypedIndividuals[0].genotype)))

        for ind in self.genotypedIndividuals:
            np.append(ret, ind.genotype.toIntArray())
        return ret

    def getNumIndivs(self) -> int:
        """DUPLICATE OF LENGTH"""

        # TODO Why is this here???
        return len(self)

    def __len__(self) -> int:
        """returns number of individuals stored in pedigree object"""
        return len(self.individuals)

    def __eq__(self, other: 'Pedigree'):
        """compares the pedigree in terms of individuals within the pedigree"""
        if (len(self) != len(other)):
            return False
        for i, b in zip(self.individuals, other.individuals):
            if (i != b):
                return False

        return True

    def __iter__(self) -> Iterator[Individual]:
        """Iterates through individuals and yields individual items """
        iter = self.individuals.items().__iter__()

        for i in iter:
            yield i[1]

    def __getitem__(self, item) -> Union[Individual,List]:
        """gets individuals"""
        if isinstance(item, list):
            return [self.individuals[i] for i in item]
        elif isinstance(item, slice):
            return [self[ii] for ii in range(*item.indices(len(self)))]
        elif isinstance(item, str):
            return self.individuals[item]
        else:
            try:
                return self.individuals[str(item)]
            except ValueError:
                raise TypeError("Wrong type given for getter:" + str(type(item)))

    def __setitem__(self, key: str, value: Individual):
        """Sets individuals """

        if (not key in self.individuals):
            value.recId= len(self.individuals)
        self.sorted = False
        self.individuals[key] = value

        if (value.founder):
            self.founders[value.id] = value

    def setIndividualAsGenotyped(self, id: str):
        ind = self[id]

        if (not ind.id in self.genotypedIndividuals):
            self.genotypedIndividuals[ind.id] = ind


    def addGenotypesFromFile(self, file: str, initAll = False):
        """Adds genotype information to corresponding animals in pedigree from file

        will overwrite corresponding information already present

        if InitAll is present - will overwrite all genotype information for all animals
        """
        size = 0
        # with open(file, 'r').readlines() as f:
        f = open(file, 'r')
        for l in f.readlines():
            t = l.strip().split(" ")

            if (not t[0] in self.individuals):
                print("Warning animal %s not in Pedigree, will be added as founder"), t[0]
                self[t[0]] = Individual('0', '0', '0', True, 0)

            g = PyGenotype(np.array(t[1:],dtype=int))
            self.individuals[t[0]].genotype = g
            self.individuals[t[0]].inconsistencies = np.zeros(len(g))
            self.genotypedIndividuals[t[0]] = self[t[0]]
            if (size == 0):
                size = len(t) - 1

        f.close()
        if initAll:
            empty = np.full(size, fill_value=MISSINGGENOTYPECODE)
            for ind in self:
                if ind.genotype is None:
                    ind.genotype = PyGenotype(empty)
                    ind.inconsistencies = np.zeros(size)
                if (len(ind.haplotypes) == 0):
                    ind.haplotypes.append(PyHaplotype(empty))
                    ind.haplotypes.append(PyHaplotype(empty))



    def compareToTrueFile(self, file: str, ids = None):
        """Returns yield and accuracy of genotype information for pedigree compared to a specified true file"""
        # with open(file, 'r').readlines() as f:
        if ids is None: ids = [ind for ind in self.individuals.keys()]
        f = open(file, 'r')

        yieldCount = 0
        diffs = 0
        totalLength = 0
        for l in f.readlines():
            t = l.strip().split(" ")

            g = PyGenotype(np.array(t[1:],dtype=int))

            if (t[0] in ids and t[0] in self.individuals):
                comp = self.individuals[t[0]].genotype
                yieldCount += comp.countNotMissing()
                totalLength += len(comp)


                diffs += comp.countNotEqualExcludeMissing(g)


        yieldRet = float(yieldCount) / totalLength
        accuracy = 1 - float(diffs) / yieldCount

        f.close()

        return (yieldRet, accuracy)


    def compareToTrueFilePhase(self, file: str, ids = None):
        """Returns yield and accuracy of genotype information for pedigree compared to a specified true file"""
        # with open(file, 'r').readlines() as f:
        if ids is None: ids = [ind for ind in self.individuals.keys()]
        f = open(file, 'r')

        yieldCount = 0
        diffs = 0
        totalLength = 0
        lines = dict()
        for l in f.readlines():
            t = l.strip().split(" ")

            g = PyHaplotype(t[1:])

            if (t[0] in ids and t[0] in self.individuals):
                if t[0] not in lines :
                    lines[t[0]] = g
                else:
                    g0 = lines.pop(t[0]) #This also removes it from the dict.
                    g1 = g

                    comp0 = self.individuals[t[0]].haplotypes[0]
                    comp1 = self.individuals[t[0]].haplotypes[1]
                    yieldCount += comp0.countNotMissing()
                    yieldCount += comp1.countNotMissing()
                    totalLength += len(comp0) + len(comp1)

                    diffsAlign = comp0.countNotEqualExcludeMissing(g0) + comp1.countNotEqualExcludeMissing(g1)
                    diffsNot = comp0.countNotEqualExcludeMissing(g1) + comp1.countNotEqualExcludeMissing(g0)
                    diffs += min(diffsAlign, diffsNot)

        yieldRet = float(yieldCount) / totalLength
        if yieldCount != 0 : accuracy = 1 - float(diffs) / yieldCount
        else: accuracy = -1 
        f.close()

        return (yieldRet, accuracy)


    def addGenotypesFromFileFast(self, file: str, initAll = False):
        size = 0
        # with open(file, 'r').readlines() as f:
        f = open(file, 'r')

        x = np.loadtxt(file, dtype=str)

        for t in x:
            # t = l.strip().split(" ")

            if (not t[0] in self.individuals):
                print("Warning animal %s not in Pedigree, will be added as founder"), t[0]
                self[t[0]] = Individual('0', '0', '0', True, 0)

            g = PyGenotype(t[1:])
            self.individuals[t[0]].genotype = g
            self.individuals[t[0]].inconsistencies = np.zeros(len(g))
            self.genotypedIndividuals[t[0]] = self[t[0]]
            if (size == 0):
                size = len(t) - 1

        f.close()
        # if initAll:
        #     empty = np.full(size, fill_value=MISSINGGENOTYPECODE)
        #     for ind in self:
        #         if ind.genotype is None:
        #             ind.genotype = Genotype(empty)
        #             ind.inconsistencies = np.zeros(size)
        #         if (len(ind.haplotypes) == 0):
        #             ind.haplotypes.append(Haplotype(empty))
        #             ind.haplotypes.append(Haplotype(empty))

    def addGenotypesFromArray(self, array: np.ndarray, initAll= False):
        size = 0
        for t in array:
            if (not t[0] in self.individuals):
                print("Warning animal %s not in Pedigree, will be added as founder" % t[0])
                self[t[0]] = Individual('0', '0', '0', True, 0)

            g = PyGenotype(t[1:])
            self.individuals[t[0]].genotype = g
            self.individuals[t[0]].inconsistencies = np.zeros(len(g))
            self.genotypedIndividuals[t[0]] = self[t[0]]
            if (size == 0):
                size = len(t[1:])
        if initAll:
            empty = np.full(size, fill_value=MISSINGGENOTYPECODE)
            for ind in self:
                if ind.genotype is None:
                    ind.genotype = PyGenotype(empty)
                    ind.inconsistencies = np.zeros(size)

    def addPhaseFromFile(self, file: str, initAll= False, overwrite=False):
        '''Adds phase information from alphasuite format file'''
        size = 0
        with open(file, 'r') as f:
            for l in f:
                t = re.split('\s+', l.strip())

                if (not t[0] in self.individuals):
                    print("Warning animal %s not in Pedigree, will be added as founder" % t[0])
                    self[t[0]] = Individual('0', '0', '0', True, 0)

                h = PyHaplotype(t[1:])
                ind = self.individuals[t[0]]
                if overwrite and len(ind.haplotypes) == 2:
                    ind.haplotypes = []
                ind.haplotypes.append(h)
                if (size == 0):
                    size = len(t[1:])
        if initAll:
            empty = np.full(size, fill_value=MISSINGGENOTYPECODE)
            for ind in self:
                if ind.haplotypes[0] is None:
                    ind.haplotypes.insert(0, PyHaplotype(empty))
                    ind.haplotypes.insert(1, PyHaplotype(empty))

    def addPhaseFromArray(self, array: np.ndarray, initAll = False):
        size = 0
        hCount = 0
        for t in array:
            if (not t[0] in self.individuals):
                print("Warning animal %s not in Pedigree, will be added as founder" % t[0])
                self[t[0]] = Individual('0', '0', '0', True, 0)

                h = PyHaplotype(t[1:])

            if (hCount == 2): hCount = 0
            self.individuals[t[0]].haplotypes[hCount] = h
            hCount += 1
            if (size == 0):
                size = len(t[1:])
        if initAll:
            empty = np.full(size, fill_value=MISSINGGENOTYPECODE)
            for ind in self:
                if ind.haplotypes[0] is None:
                    ind.haplotypes[0] = PyHaplotype(empty)
                    ind.haplotypes[1] = PyHaplotype(empty)

    def getMatePairs(self: 'Pedigree'):
        """Gets pairs of mates that are in the pedigree"""

        checked = {}
        for ind in self.individuals.items():

            for off in ind.offsprings:

                if off.sire == ind:

                    pair = Utils.generateParing(ind.recId, off.dam.recId)

                    if pair in checked:
                        checked[pair].offspring.append(off)
                    else:
                        checked[pair] = Family(ind, off.dam, off)

                elif off.dam == ind:
                    pair = Utils.generateParing(ind.recId, off.sire.recId)

                    if pair in checked:
                        checked[pair].offspring.append(off)
                    else:
                        checked[pair] = Family(off.sire, ind, off)
        return checked

    def sortPedigree(self: 'Pedigree') -> 'Pedigree':

        """Returns a new pedigree that is sorted """

        new = Pedigree()
        seen = {}
        self.generations = []
        new.founders = self.founders
        seen['0'] = True
        new['0'] = self['0']
        currentGen = 0
        # new['0'] = Individual('0', '0', '0', True, 0)
        for i in self.founders:
            self.__checkOffspring(self.founders[i], seen, self.generations, currentGen)

        new.generations = self.generations

        # self.individuals = OrderedDict()
        for g in self.generations:
            for animal in g:
                new.individuals[animal.id] = animal

                if (animal.id in self.genotypedIndividuals):
                    new.genotypedIndividuals[animal.id] = animal

        new.sorted = True
        return new

    def findMendelianInconsistencies(self: 'Pedigree', threshold = 0.05, file = None):
        """Function computes the inconsistencies properties across the pedigree"""
        snpChanges = 0
        countChanges = 0

        sireRemoved = False
        damRemoved = False

        if not self.sorted:
            print("WARNING - Pedigree is not sorted - MendelianInconsistencies might be unreliable")

        for ind in self:

            if (ind.founder):
                continue
            mend = ind.getInconsistencies()
            sireIncon = mend.paternalInconsistent.count(True)
            ind.sire.inconsistenciesCount += sireIncon
            damIncon = mend.maternalInconsistent.count(True)
            ind.dam.inconsistenciesCount += damIncon

            if (float(sireIncon) / len(ind.genotype) > threshold):
                countChanges += 1
                ind.sire.removeOffspring(ind, self['0'])
                sireRemoved = True

            if (float(damIncon) / len(ind.genotype) > threshold):
                countChanges += 1
                ind.dam.removeOffspring(ind, self['0'])
                damRemoved = True

            if (not sireRemoved):
                count = 0
                for i, c in zip(mend.paternalInconsistent, mend.paternalConsistent):
                    if i:
                        ind.sire.inconsistencies[count] += 1
                    count += 1
                    if c:
                        ind.sire.inconsistencies[count] -= 1
                count += 1

            if (not damRemoved):
                count = 0
                for i, c in zip(mend.maternalInconsistent, mend.maternalConsistent):
                    if i:
                        ind.dam.inconsistencies[count] += 1
                    if c:
                        ind.dam.inconsistencies[count] -= 1
                    count += 1

        for ind in self:
            if ind.founder:
                continue
            for i in range(0, len(ind.genotype)):
                if ind.mend.individualInconsistent[i]:
                    snpChanges += 1

                    if (ind.sire.inconsistencies[i] > ind.dam.inconsistencies[i]):
                        ind.genotype[i] = MISSINGGENOTYPECODE
                        ind.sire.genotype[i] = MISSINGGENOTYPECODE
                    elif (ind.sire.inconsistencies[i] < ind.dam.inconsistencies[i]):
                        ind.genotype[i] = MISSINGGENOTYPECODE
                        ind.dam.genotype[i] = MISSINGGENOTYPECODE
                    else:
                        ind.genotype[i] = MISSINGGENOTYPECODE
                        ind.sire.genotype[i] = MISSINGGENOTYPECODE
                        ind.dam.genotype[i] = MISSINGGENOTYPECODE

    #     TODO think about the case of having only one parent

    def __checkOffspring(self: 'Pedigree', animal: Individual, seen: [bool], generations: [], currentGen: int):
        if (not (animal.id == '0')):
            seen[animal.id] = True

            if currentGen > len(generations) - 1:
                generations.append([])

            animal.generation = currentGen
            generations[currentGen].append(animal)
            # file.write(animal.id +" " + animal.sireId + " " + animal.damId+'\n')
            for off in animal.offsprings:
                if (off.sireId in seen and off.damId in seen):
                    m = max(off.sire.generation, off.dam.generation)
                    self.__checkOffspring(off, seen, generations, m + 1)


class Family:
    def __init__(self, sire: Individual, dam: Individual, off: Individual):
        """Class to define a family in the Pedigree"""
        self.sire = sire
        self.dam = dam
        self.children = set()
        self.children.add(off)


infile = "pedigree.txt"
# infile = "merge_illumina"
outfile = "ped.out"

# o = open(outfile,'w')

# # ped = Pedigree(plinkFile=infile)
# ped = Pedigree(file=infile)
# y = ped.sortPedigree()
#
# print(y)
# o.write(y.__str__())
