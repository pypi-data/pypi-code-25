import pickle
import unittest
import sys
from hap import PyHaplotype as Haplotype
from gen import PyGenotype as Genotype

class testGenotypes(unittest.TestCase):


    def testGet(self):
        # Genotype.Genotype(lock=)
        self.g = Genotype([1, 0, 2, 1, 2, 0])

        self.assertEqual(self.g[0],1)
        self.assertEqual(self.g[1], 0)
        self.assertEqual(self.g[2], 2)
        self.assertEqual(self.g[3], 1)
        self.assertEqual(self.g[4], 2)
        self.assertEqual(self.g[5], 0)

        self.assertEqual(self.g[2:6], [ 2, 1, 2, 0])

    def testSet(self):
        self.g = Genotype([1, 0, 2, 1, 2, 0])

        self.g[1] = 2
        self.assertEqual(self.g[1], 2)
        self.g[2] = 1
        self.assertEqual(self.g[2], 1)
        self.g[4] = 0
        self.assertEqual(self.g[4], 0)

    def testIfHapCompatibleTrue(self):
        self.g = Genotype([1, 0, 2, 1, 2, 0])
        hap = Haplotype([1, 0, 1, 1, 1, 0])
        self.assertTrue(self.g.isHaplotypeCompatible(hap))

    def testGenFromHaps(self):
        self.g = Genotype([2, 1, 1, 9, 2, 0])
        hap = Haplotype([1, 0, 1, 1, 1, 0])
        hap2 = Haplotype([1, 1, 0, 9, 1, 0])
        gen2 = Genotype(haplotypes=[hap,hap2])

        self.assertEqual(self.g, gen2)
        self.assertTrue(self.g.isHaplotypeCompatible(hap))



    def testIfHapCompatibleFalse(self):
        self.g = Genotype([1, 0, 2, 1, 2, 0])
        hap = Haplotype([1, 0, 0, 1, 1, 0])
        self.assertFalse(self.g.isHaplotypeCompatible(hap))

    def testCountMismatches(self):
        self.g = Genotype([1, 0, 2, 1, 2, 0])
        g2 = Genotype([1, 0, 2, 1, 1, 2])
        g3 = Genotype([0, 0, 0, 0, 0, 2])
        self.assertEqual(self.g.countMismatches(g2), 1)
        self.assertEqual(self.g.countMismatches(g3), 3)

    def testNumHet(self):
        g2 = Genotype([1, 0, 2, 1, 1, 2])
        g1 = Genotype([1, 1, 1, 1, 1, 1, 1])

        self.assertEqual(g1.numHet(), 7)
        self.assertEqual(g2.numHet(), 3)

    def testGetSubset(self):
        self.g = Genotype([1, 0, 2, 1, 2, 0])

        g2 = self.g.getSubsetGenotype(2, 5)

        self.assertEqual(g2[0], 2)
        self.assertEqual(g2[1], 1)
        self.assertEqual(g2[2], 2)
        self.assertEqual(len(g2), 3)

    def testIter(self):
        self.g = Genotype([1, 0, 2, 1, 2, 0])
        a = [1, 0, 2, 1, 2, 0]
        count = 0

        for g1,g2 in zip(self.g,a):
            self.assertEqual(g1,g2)
            count +=1

        self.assertEqual(count, len(a))




    def testSetFromOtherMissing(self):
        g1 = Genotype([1, 0, 9, 9])
        g2 = Genotype([1, 0, 2, 2])
        g1.setFromOtherIfMissing(g2)
        self.assertEqual(g1, g2)
        g1 = Genotype([1, 0, 9, 9])
        g2 = Genotype([1, 0, 1, 1])
        g1.setFromOtherIfMissing(g2)
        self.assertEqual(g1, g2)
        g1 = Genotype([1, 9, 9, 9])
        g2 = Genotype([2, 0, 1, 9])
        g3 = Genotype([1,0,1,9])
        g1.setFromOtherIfMissing(g2)
        self.assertEqual(g1, g3)

    def testSetFromHapIfMissing(self):

        g1 = Genotype([1,0,9,9])

        h1 = Haplotype([1,9,1,0])
        h2 = Haplotype([1, 0, 1, 1])

        g2 = Genotype([1,0,2,1])
        g1.setFromHaplotypesIfMissing(h1,h2)
        self.assertEqual(g1,g2)


    def testCompliment(self):

        g1 = Genotype([1, 0, 2, 2])
        h1 = Haplotype([1, 0, 1, 1])
        h2 = Haplotype([0, 0, 1, 1])
        self.assertTrue(g1.complement(h1).checkEqual(h2))

        g1 = Genotype([1, 0, 9, 2])
        h1 = Haplotype([0, 0, 1, 1])
        h2 = Haplotype([1, 0, 9, 1])
        h1comp = g1.complement(h1)

        self.assertEqual(h1comp, h2)

    # def testPickle(self):
    #     self.g = Genotype([1, 0, 2, 1, 2, 0])
    #     pickle_out = open("dict.pickle", "wb")
    #     pickle.dump(self.g, pickle_out)

    #     pickle_out.close()

    #     pickle_in = open("dict.pickle", "rb")

    #     self.g2 = pickle.load(pickle_in)
    #     pickle_in.close()

    #     self.assertEqual(self.g,self.g2)

    def testString(self):
        self.g = Genotype([1, 0, 2, 1, 2, 0])
        s = "1 0 2 1 2 0"


        sTest = str(self.g)
        self.assertEqual(s, sTest)

        self.g = Genotype([1, 0, 2, 1, 2, 1])
        s = "1 0 2 1 2 1"

        sTest = str(self.g)
        self.assertEqual(s, sTest)


    def testNotEqual(self):
        g1 = Genotype([1, 0, 9, 2])
        g2 = Genotype([1, 0, 1, 2])

        self.assertEqual(g1.countNotEqual(g2),1)

        g2 = Genotype([0, 1, 0, 0])
        self.assertEqual(g1.countNotEqual(g2), 4)


    def testNotEqualExcludeMissing(self):
        g1 = Genotype([1, 0, 9, 2])
        g2 = Genotype([1, 0, 1, 2])

        self.assertEqual(g1.countNotEqualExcludeMissing(g2),0)

        g2 = Genotype([0, 1, 0, 0])
        self.assertEqual(g1.countNotEqualExcludeMissing(g2), 3)
