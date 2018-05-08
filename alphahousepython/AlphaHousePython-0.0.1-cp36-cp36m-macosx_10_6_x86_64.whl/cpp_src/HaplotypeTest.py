import unittest

from hap import PyHaplotype as Haplotype
from gen import PyGenotype as Genotype

class testHaplotype(unittest.TestCase):


    def testGet(self):
        # Genotype.Genotype(lock=)
        self.g = Haplotype([1, 0,1, 1, 1, 0])

        self.assertEqual(self.g[0],1)
        self.assertEqual(self.g[1], 0)
        self.assertEqual(self.g[2], 1)
        self.assertEqual(self.g[3], 1)
        self.assertEqual(self.g[4], 1)
        self.assertEqual(self.g[5], 0)
        self.assertEqual(self.g[2:6], [ 1, 1, 1, 0])

    def testSet(self):
        self.g = Haplotype([1, 0, 1, 1, 1, 0])

        self.g[1] = 1
        self.assertEqual(self.g[1], 1)
        self.g[2] = 1
        self.assertEqual(self.g[2], 1)
        self.g[4] = 0
        self.assertEqual(self.g[4], 0)
        
    def testIter(self):
        self.h= Haplotype([1, 0, 1, 1, 1, 9])
        a = [1, 0, 1, 1, 1, 9]
        count = 0
        for g1, g2 in zip(self.h, a):
            self.assertEqual(g1, g2)
            count += 1

        self.assertEqual(count,len(a))


    def testSetFromGenotypeIfMissing(self):
        self.h = Haplotype([1, 0, 1, 1, 9, 9])
        g = Genotype([2, 1 ,1,1, 0, 0])
        h2 =  Haplotype([1, 0, 1, 1, 0, 0])
        self.h.setFromGenotypeIfMissing(g)

        self.assertEqual(h2, self.h)


    def testSetFromOtherIfMissing(self):
        self.h = Haplotype([1, 0, 1, 1, 9, 9])
        h2 = Haplotype([0, 0, 1, 1, 1, 0])
        h3 = Haplotype([1, 0, 1, 1, 1, 0])
        self.h.setFromOtherIfMissing(h2)
        self.assertEqual(h3, self.h)


    def testString(self):
        self.h = Haplotype([1, 0, 1, 1, 1, 0])
        s = "1 0 1 1 1 0"


        sTest = str(self.h)
        self.assertEqual(s, sTest)

        self.h = Haplotype([1, 0, 1, 1, 1, 1])
        s = "1 0 1 1 1 1"

        sTest = str(self.h)
        self.assertEqual(s, sTest)

    def testCountNotEqualExcludeMissing(self):
        self.h = Haplotype([1, 9, 9, 1, 1, 0])
        self.h2 = Haplotype([1, 2, 9, 0, 1, 0])

        val = self.h.countNotEqualExcludeMissing(self.h2)

        self.assertEqual(val, 1)
