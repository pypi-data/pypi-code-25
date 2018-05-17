import os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import peakutils
import pandas as pd

from baseq.drops.apa.scaner import scan

def scan_genes(genome, bam, name):
    """Example function with types documented in the docstring.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Examples:
        Examples should be written in doctest format, and should illustrate how
        to use the function.

    Returns:
        bool: The return value. True for success, False otherwise.

    """

    from baseq.bam import BAMTYPE
    from baseq.rna.gtf.gencode import read_gencode

    df = read_gencode(genome, "UTR")
    df['length'] = df.end - df.start
    df = df.sort_values(by=['length'])
    df = df.groupby("gene").last()
    df = df.loc[df.length>1000]
    bam = BAMTYPE(bam)

    import multiprocessing as mp
    pool = mp.Pool(processes=20)
    results = []
    for index, row in df.iterrows():
        results.append(pool.apply_async(scan, (bam, index, row['chr'], row['start'], row['end'], 50)))
    pool.close()
    pool.join()

    results = [x.get() for x in results]
    results = [y for x in results for y in x]
    results = [df.loc[x[0],:].tolist() + x  for x in results]
    df_peaks = pd.DataFrame(results, columns=["chr", "start", 'end', 'strand', 'transc',
                                              'exon', 'length', 'gene', 'pos', 'mean_depth',
                                              "mid", "left", "right", "counts"])

    df_peaks = df_peaks.drop(columns=["transc", 'exon'])
    file_tsv = "peaks.{}.txt".format(name)
    file_xls = "peaks.{}.xls".format(name)
    df_peaks.to_csv("peaks.{}.txt".format(name), sep="\t")
    df_peaks.to_excel("peaks.{}.xls".format(name))
    print("[info] The peaks files are write to: {}/{}".format(file_tsv, file_xls))