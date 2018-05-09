import time

from Genotype import MISSINGGENOTYPECODE, Genotype
from PedigreeHolder import Pedigree,Individual
import numpy as np
# import scipy as sp
import typing
log1 = 0
loge = np.log(np.exp(-5))
log5 = np.log(0.5)
logd = loge


# Global variables defined for heuristic geneprob
heuristicTrace = np.empty((3,3))
heuristicTrace[0,:] = (log1,log5,loge)
heuristicTrace[0,:] = (loge,log5,log1)
heuristicTrace[0,:] = (log1,log5,loge)

heuristicTraceNoSeg = np.empty((3,4),dtype=np.float64)
heuristicTraceNoSeg[0, :] = (log1, log5, log5, loge)
heuristicTraceNoSeg[1, :] = (loge, log5, log5, log1)
heuristicTraceNoSeg[2, :] = (loge, log5, log5, log1)

heuristicTraceSeg = np.empty((2,2,4),dtype=np.float64)
heuristicTraceSeg[0,0,:] = (log1, log1, logd, logd)
heuristicTraceSeg[1,0,:] = (logd, logd, log1, log1)
heuristicTraceSeg[0, 1 ,:]= (log1, logd, log1, logd)
heuristicTraceSeg[0,1,:] = (logd, log1, logd, log1)

DISTANCETHRESHOLD = 15

def heuristicGenerob(ped : Pedigree):

    for ind in ped:

        for (i,g) in enumerate(ind.genotype):

            genosProbs = np.zeros(3,dtype=np.float64)

            if (g != MISSINGGENOTYPECODE): continue

            for off in ind.offsprings:

                offG = off.genotype[i]

                if offG == MISSINGGENOTYPECODE: continue

                if (off.sire == ind):
                    sire = True
                    e = 0
                else:
                    sire = False
                    e = 1

                if (offG == 1):

                    p = off.haplotypes[e][i]

                    if (p != MISSINGGENOTYPECODE):
                        genosProbs[:]= genosProbs[:] + heuristicTrace[:,p]

                    else:
                        if (sire):
                            gOtherParent = off.dam.genotype[i]
                        else:
                            gOtherParent = off.sire.genotype[i]

                        if (gOtherParent == 0 or gOtherParent == 1):
                            p = 1 - gOtherParent / 2
                            genosProbs[:] = genosProbs[:] + heuristicTrace[:,p]
                else:
                    genosProbs[:]  = genosProbs[:] + heuristicTrace[:,offG]

            indexes = np.argpartition(genosProbs, -2)[-2:] #get two largest indexes as a list
            largest = genosProbs[indexes[0]]
            secondLargest = genosProbs[indexes[1]]
            pos = indexes[0]

            if (largest - secondLargest > DISTANCETHRESHOLD):
                ind.genotype[i] = pos



def heuristicMLP(ped : Pedigree):
    peelDown(ped)
    updateSeg(ped)
    peelUp(ped)
    
    
def peelDown(ped : Pedigree):

    parentPhase = np.zeros((2,2), dtype=np.int8)
    parentGeno = np.zeros((2), dtype=np.int8)

    for ind in ped:

        ind.setSegToMissing()
        if ind.founder: continue

        for i,g in enumerate(ind.genotype):
            parentPhase[0,0] = ind.sire.haplotypes[0][i]
            parentPhase[0,1] = ind.sire.haplotypes[1][i]
            parentPhase[1,0] = ind.dam.haplotypes[0][i]
            parentPhase[1,1] = ind.dam.haplotypes[1][i]
            parentGeno[0] = ind.sire.genotype[i]
            parentGeno[1] = ind.dam.genotype[i]

            for h in range(0,2):
                if parentGeno[h] == 2:

                    ind.haplotypes[h][i] = 1
                elif parentGeno[h] == 0:
                    ind.haplotypes[h][i] = 0

                elif parentGeno[h] == 1:
                    if (parentPhase[h,1] != MISSINGGENOTYPECODE and parentPhase[h,1] != MISSINGGENOTYPECODE):
                        seg = ind.seg[i,h]
                        if seg != MISSINGGENOTYPECODE:
                            ind.haplotypes[h][i] = parentPhase[h,seg]

        ind.makeIndividualGenotypeFromPhase()
        ind.makeIndividualPhaseCompliment()

def peelUp(ped : Pedigree):

    for ind in ped.GenotypedIndividuals:

        for i, g in ind.genotype:
            phaseProbs = np.zeros(ind.genotype.length)

            for off in ind.offsprings:
                offG = off.genotype[i]

                if offG != MISSINGGENOTYPECODE: continue

                if (off.sire == ind):
                    e = 0
                    sire = True
                else:
                    e = 1
                    sire = False

                childSeg= ind.seg[i,e]

                if (childSeg != MISSINGGENOTYPECODE):
                    childPhase = ind.haplotypes[e][i]
                    if (childPhase != MISSINGGENOTYPECODE):
                        phaseProbs[:]=  phaseProbs[:] + heuristicTraceSeg[childPhase,childSeg, :]
                else:

                    if g == 1:
                        p = off.haplotypes[e][i]

                        if (p!= MISSINGGENOTYPECODE):
                            phaseProbs[:] = phaseProbs[:]+ heuristicTraceNoSeg[g,:]

                    else:
                        if (sire):
                            g = off.dam.genotype[i]
                        else:
                            g = off.sire.genotype[i]

                        if (g == MISSINGGENOTYPECODE): continue

                        phaseProbs[:] = phaseProbs[:] + heuristicTraceNoSeg[g,:]

            indexes = np.argpartition(phaseProbs, -2)[-2:] #get two largest indexes as a list
            largest = phaseProbs[indexes[0]]
            secondLargest = phaseProbs[indexes[1]]
            pos = indexes[0]
            secondPos = indexes[1]


            if (largest - secondLargest) > 15-1:
                if pos == 0:
                    ind.genotype[i] = 0
                    ind.phase[0][i] = 0
                    ind.phase[1][i] = 0

                elif pos == 1:
                    ind.genotype[i] = 1
                    ind.phase[0][i] = 0
                    ind.phase[1][i] = 1
                elif pos == 2:
                    ind.genotype[i] = 1
                    ind.phase[0][i] = 1
                    ind.phase[1][i] = 0
                elif pos == 3:
                    ind.genotype[i] = 2
                    ind.phase[0][i] = 1
                    ind.phase[1][i] = 1
            else:
                genosProbs = (phaseProbs[0], np.max(phaseProbs[1:]))
                indexes = np.argpartition(genosProbs, -2)[-2:] #get two largest indexes as a list
                largest = genosProbs[indexes[0]]
                secondLargest = genosProbs[indexes[1]]
                pos = indexes[0]

                if (largest - secondLargest) > DISTANCETHRESHOLD:
                    ind.genotype[i] = pos


def updateSeg(ped : Pedigree):

    threshold = 3


    for ind in ped:
        if ind.founder: continue



        for i,g in enumerate(ind.genotype):
            genos = (ind.sire.genotype[i], ind.dam.genotype[i])
            if (np.mod(genos[0],2) == 0 and np.mod(genos[1],2) == 0): continue

            if (ind.haplotypes[0][i] != MISSINGGENOTYPECODE and ind.haplotypes[1][i] != MISSINGGENOTYPECODE):

                parents = ind.getParentArray()
                for e in range(0,2):
                    parent = parents[e]
                    if (genos[e] == 1):
                        phase = (parent.haplotypes[0][i],parent.haplotypes[1][i])


                        if (not all(phase) == 9):
                            if (ind.haplotypes[e][i] == phase[0]):
                                ind.seg[i,e] = 1 #TODO originally 1 and 2 _TEST! MIGHT NEED TO BE 0, 1
                            elif ind.haplotypes[e][i] == phase[1]:
                                ind.seg[i,e] = 2

        for i in range(0,2):

            startLoc = 0
            lastLoc = 0
            currentSeg = -1
            numConsistent = 0


            for h in range(0, ind.genotype.length):
                if ind.seg[h,i] != MISSINGGENOTYPECODE:
                    lastLoc = h
                    numConsistent += 1
                else:
                    if (numConsistent > threshold):
                        ind.seg[startLoc:lastLoc,i] = currentSeg
                    else:
                        ind.seg[startLoc:lastLoc,i] = MISSINGGENOTYPECODE
                    startloc = h
                    lastLoc = h
                    currentSeg = ind.seg[h,i]
                    numConsistent = 1

            lastLoc = ind.genotype.length

            if (numConsistent > threshold):
                ind.seg[startLoc:lastLoc,i] = currentSeg
            else:
                ind.seg[startLoc:lastLoc,i] = MISSINGGENOTYPECODE







# ped = Pedigree(file='recoded-pedigree.txt')

# print("READ IN PED")
# start = time.time()
# ped.addGenotypesFromFile('genos.txt',initAll=True)
# end = time.time()
# print("time" + str(end - start))
# # ped.addGenotypesFromFile('genoTest.txt',initAll=True)
# print("READ IN geno")


# start = time.time()
# # heuristicMLP(ped)
# heuristicGenerob(ped)
# end = time.time()
# print("time" + str(end - start))

