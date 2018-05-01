#!/usr/bin/env python

"""Similarity code tentative cognates in a word list"""

import numpy
import itertools

import pickle

import sys
import argparse

from clldutils.path import Path
from pycldf.dataset import Wordlist

from lingpy.compare.lexstat import LexStat
from lingpy.algorithm import extra
import infomapcog.distances as dist


def infomap(x, y):
    """Cluster using infomap.

    [https://github.com/lingpy/lingpy/blob/0432b7b845064223dcbb6be4e31430ed5d752fb1/lingpy/compare/lexstat.py#L584]
    """
    return extra.infomap_clustering(
        y, x, list(range(len(x))), revert=True)


dataset = Wordlist.from_metadata("../cldf/Wordlist-metadata.json")
primary_table = dataset[dataset.primary_table]
def to_bonkers_internal_lingpy_format(table):
    i = 0
    for row in table.iterdicts():
        if i == 0:
            headers = ['ID', 'Language_ID', 'Parameter_ID', 'Value', 'Segments', 'Comment', 'Source']
            yield i, ['ID', 'DOCULECT', 'CONCEPT', 'IPA', 'TOKENS', 'COMMENT', 'SOURCE']
        i += 1
        yield i, [row[key] for key in headers]

lex = LexStat({i: row
               for i, row in to_bonkers_internal_lingpy_format(primary_table)})
lex.cluster(method="lexstat", threshold=0.55, cluster_method="infomap", guess_threshold=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("cldf", default=Path("Wordlist-metadata.json"), nargs="?",
                        type=Path,
                        help="CLDF word list to analyse")
    parser.add_argument("--lodict", default=None,
                        type=argparse.FileType('rb'),
                        help="Phonetic segment similiarity dictionary")
    args = parser.parse_args()

    if args.lodict is None:
        lodict = {}
    else:
        lodict = pickle.load(args.lodict)

    dataset = Wordlist.from_metadata(args.cldf)
    primary_table = dataset[dataset.primary_table]

    words_for = {}
    for row in primary_table.iterdicts():
        concept = row["Parameter_ID"]
        words = words_for.setdefault(concept, {})
        words[row["ID"]] = row["Segments"]

    for concept, words in words_for.items():
        distmat = numpy.zeros((len(words), len(words)))
        for (i1, (id1, form1)), (i2, (id2, form2)) in (
                itertools.combinations(enumerate(words.items()), 2)):
            score, align = dist.needleman_wunsch(
                form1, form2, lodict=lodict, gop=-2.5, gep=-1.75)
            print(align)
            distmat[i2, i1] = distmat[i1, i2] = 1 - (1/(1 + numpy.exp(-score)))
        print(distmat)

    LexStat.cluster(external_function=infomap)
    LexStat._get_matrices

    function = self._distance_method(
                method, scale=scale, factor=factor,
                restricted_chars=restricted_chars, mode=mode, gop=gop,
                restriction=restriction, external_scorer=kw['external_scorer'])

