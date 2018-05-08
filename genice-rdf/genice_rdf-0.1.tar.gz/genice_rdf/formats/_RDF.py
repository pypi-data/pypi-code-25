# coding: utf-8
"""
RDF.
"""

import itertools as it
import numpy as np
import pairlist as pl
from collections import defaultdict


def hist2rdf(hist, vol, natoms, binw, nbin):
    rdf = np.zeros(nbin)
    for r,c in hist.items():
        if r < nbin:
            rdf[int(r)] = c
    if len(natoms) == 1:
        mult   = natoms[0]**2 / 2
    else:
        mult   = natoms[0]*natoms[1]
    ri = np.arange(nbin)*binw + binw/2
    vshell = 4*np.pi*ri**2*binw
    rdf *= vol / (vshell*mult)
    return rdf
    


def hook7(lattice):
    lattice.logger.info("Hook7: Output radial distribution functions.")
    lattice.logger.info("  Total number of atoms: {0}".format(len(lattice.atoms)))
    binw = 0.003
    nbin = 300
    cellmat = lattice.repcell.mat
    rpos = defaultdict(list)
    for atom in lattice.atoms:
        resno, resname, atomname, position, order = atom
        rpos[atomname].append(lattice.repcell.abs2rel(position))
    rdf = []
    rdfname = []
    volume =  np.linalg.det(lattice.repcell.mat)
    grid = pl.determine_grid(cellmat,binw*nbin)
    lattice.logger.info("  Accelerate using pairlist.")
    for atomname in rpos:
        ra = rpos[atomname] = np.array(rpos[atomname])
        na = ra.shape[0]
        lattice.logger.info("  Pair {0}-{0}".format(atomname))
        i,j,delta = pl.pairs_fine(ra, binw*nbin, cellmat, grid, distance=True, raw=True)
        delta = np.floor(delta/binw)
        hist = dict(zip(*np.unique(delta, return_counts=True)))
        rdfname.append((atomname, atomname))
        rdf.append(hist2rdf(hist, volume, (na,), binw, nbin))
    for a, b in it.combinations(rpos, 2):
        ra = rpos[a]
        rb = rpos[b]
        na = ra.shape[0]
        nb = rb.shape[0]
        lattice.logger.info("  Pair {0}-{1}".format(a,b))
        i,j,delta = pl.pairs_fine_hetero(ra, rb, binw*nbin, cellmat, grid, distance=True, raw=True)
        delta = np.floor(delta/binw)
        hist = dict(zip(*np.unique(delta, return_counts=True)))
        rdfname.append((a,b))
        rdf.append(hist2rdf(hist, volume, (na,nb), binw, nbin))
    print("# r/nm ", "\t".join(["{0}-{1}".format(*name) for name in rdfname]))
    for i in range(1,nbin):
        values = [i*binw]+[r[i] for r in rdf]
        print("\t".join(["{0:.3f}".format(v) for v in values]))
    lattice.logger.info("Hook7: end.")
    

hooks = {7:hook7}
