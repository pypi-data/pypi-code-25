from functools import partial
import numpy as np
import pandas as pd
from scipy.linalg import toeplitz
from scipy.signal import fftconvolve


def lattice_pdist_frequencies(n, points):
    """
    Distribution of pairwise 1D distances among a collection of distinct
    integers ranging from 0 to n-1.

    Parameters
    ----------
    n : int
        Size of the lattice on which the integer points reside.
    points : sequence of int
        Arbitrary integers between 0 and n-1, inclusive, in any order but 
        with no duplicates.

    Returns
    -------
    h : 1D array of length n
        h[d] counts the number of integer pairs that are exactly d units apart

    Notes
    -----
    This is done using a convolution via FFT. Thanks to Peter de Rivaz; see
    <http://stackoverflow.com/questions/42423823/distribution-of-pairwise-
    distances-between-many-integers>.
    
    """
    if len(np.unique(points)) != len(points):
        raise ValueError("Integers must be distinct.")
    x = np.zeros(n); x[points] = 1
    return np.round(fftconvolve(x, x[::-1], mode='full')).astype(int)[-n:]


def count_bad_pixels_per_diag(n, bad_bins):
    """
    Efficiently count the number of bad pixels on each upper diagonal of a
    matrix assuming a sequence of bad bins forms a "grid" of invalid pixels.
    
    Each bad bin bifurcates into two a row and column of bad pixels, so an 
    upper bound on number of bad pixels per diagonal is 2*k, where k is the 
    number of bad bins. For a given diagonal, we need to subtract from this
    upper estimate the contribution from rows/columns reaching "out-of-bounds"
    and the contribution of the intersection points of bad rows with bad
    columns that get double counted.
    
    o : bad bin
    * : bad pixel
    x : intersection bad pixel
    $ : out of bounds bad pixel

         $    $     $
     *--------------------------+    
      *  *    *     *           |    
       * *    *     *           |    
        **    *     *           |    
         o****x*****x***********|$    
          *   *     *           |    
           *  *     *           |    
            * *     *           |    
             o******x***********|$    
              *     *           |    
               *    *           |    
                *   *           |    
                 *  *           |    
          gaps        * *           |    
                   **           |    
                    o***********|$    
                     *          |    
                      *         |    
    
    Parameters
    ----------
    n : int
        total number of bins
    bad_bins : 1D array of int
        sorted array of bad bin indexes

    Returns
    -------
    dcount : 1D array of length n
        dcount[d] == number of bad pixels on diagonal d
    
    """
    k = len(bad_bins)
    dcount = np.zeros(n, dtype=int)

    # Store all intersection pixels in a separate array
    # ~O(n log n) with fft
    ixn = lattice_pdist_frequencies(n, bad_bins)
    dcount[0] = ixn[0]

    # Keep track of out-of-bounds pixels by squeezing left and right bounds
    # ~O(n)
    pl = 0
    pr = k
    for diag in range(1, n):
        if pl < k:
            while (bad_bins[pl] - diag) < 0:
                pl += 1
                if pl == k:
                    break
        if pr > 0:
            while (bad_bins[pr-1] + diag) >= n:
                pr -= 1
                if pr == 0:
                    break
        dcount[diag] = 2*k - ixn[diag] - pl - (k - pr)
    return dcount


def count_all_pixels_per_diag(n):
    """
    Total number of pixels on each upper diagonal of a square matrix.

    Parameters
    ----------
    n : int
        total number of bins (dimension of square matrix)

    Returns
    -------
    dcount : 1D array of length n
        dcount[d] == total number of pixels on diagonal d

    """
    return np.arange(n, 0, -1)


def make_diag_table(bad_mask, span1, span2):
    """
    Compute the total number of elements ``n_elem`` and the number of bad 
    elements ``n_bad`` per diagonal for a single contact area encompassing 
    ``span1`` and ``span2`` on the same genomic scaffold (cis matrix).

    Follows the same principle as the algorithm for finding contact areas for
    computing scalings.

    Parameters
    ----------
    bad_mask : 1D array of bool
        Mask of bad bins for the whole genomic scaffold containing the regions
        of interest.
    span1, span2 : pair of ints
        The bin spans (not genomic coordinates) of the two regions of interest.

    Returns
    -------
    diags : pandas.DataFrame
        Table indexed by 'diag' with columns ['n_elem', 'n_valid'].

    """
    where = np.flatnonzero
    def _make_diag_table(n_bins, bad_locs):
        diags = pd.DataFrame(index=pd.Series(np.arange(n_bins), name='diag'))
        diags['n_elem'] = count_all_pixels_per_diag(n_bins)
        diags['n_valid'] = (count_all_pixels_per_diag(n_bins) - 
                            count_bad_pixels_per_diag(n_bins, bad_locs))
        return diags
    
    if span1 == span2:
        lo, hi = span1
        diags = _make_diag_table(hi - lo, where(bad_mask[lo:hi]))
    else:
        lo1, hi1 = span1
        lo2, hi2 = span2
        if lo2 <= lo1:
            lo1, lo2 = lo2, lo1
            hi1, hi2 = hi2, hi1
        diags = (
            _make_diag_table(hi2 - lo1, where(bad_mask[lo1:hi2]))
                .subtract(_make_diag_table(lo2 - lo1, where(bad_mask[lo1:lo2])), 
                          fill_value=0)
                .subtract(_make_diag_table(hi2 - hi1, where(bad_mask[hi1:hi2])), 
                          fill_value=0)            
        )
        if hi1 < lo2:
            diags.add(_make_diag_table(lo2 - hi1, where(bad_mask[hi1:lo2])), 
                      fill_value=0)
        diags = diags[diags['n_elem'] > 0]
    return diags.astype(int)


def make_diag_tables(clr, supports):
    where = np.flatnonzero
    diag_tables = {}
    for i, region in enumerate(supports):
        if len(region) == 3:
            chrom, start1, end1 = region
            start2, end2 = start1, end1
        elif len(region) == 5:
            chrom, start1, end1, start2, end2 = region
        bins = clr.bins().fetch(chrom).reset_index(drop=True)
        bad_mask = np.array(bins['weight'].isnull())
        lo1, hi1 = clr.extent((chrom, start1, end1))
        lo2, hi2 = clr.extent((chrom, start2, end2))
        co = clr.offset(chrom)
        lo1 -= co
        lo2 -= co
        hi1 -= co
        hi2 -= co
        dt = make_diag_table(bad_mask, [lo1, hi1], [lo2, hi2])
        diag_tables[i] = dt
    return diag_tables


def normalize_supports(clr, supports):
    support_strs = []
    normalized = []
    for i, region in enumerate(supports):
        if len(region) == 1:
            chrom, = region
            start, end = 0, clr.chromsizes[chrom]
            normalized.append((chrom, start, end))
            support_strs.append('{}:{}-{}'.format(chrom, start1, end1))
        elif len(region) == 3:
            chrom, start, end = region
            normalized.append((chrom, start, end))
            support_str = '{}:{}-{}'.format(chrom, start, end)
        elif len(region) == 5:
            chrom, start1, end1, start2, end2 = region
            normalized.append((chrom, start1, end1, start1, end2))
            support_str = '{}:{}-{}|{}-{}'.format(chrom, start1, end1, start2, end2)
        else:
            raise ValueError("Regions must be sequences of length 1, 3 or 5")
    return normalized, support_strs


 def cis_expected(clr, supports, chunksize=10000000, use_lock=False, 
                  ignore_diags=2, map=map):
    """
    Compute the mean signal along diagonals of one or more regional blocks of
    intra-chromosomal contact matrices. Typically used as a background model 
    for contact frequencies on the same polymer chain. 

    Parameters
    ----------
    clr : cooler.Cooler
        Input Cooler
    regions : iterable of genomic regions or pairs of regions
        Iterable of genomic region strings or 3-tuples, or 5-tuples for pairs
        of regions
    field : str, optional
        Which values of the contact matrix to aggregate. This is currently a
        no-op. *FIXME*
    chunksize : int, optional
        Size of dask chunks.

    Returns
    -------
    Dataframe of diagonal statistics, indexed by region and diagonal number

    """    
    from cooler.tools import split, partition

    def process_chunk(clr, supports, span):
        lo, hi = span
        print(lo, hi)
        bins = clr.bins()[:]

        # annotate pixels
        pixels = clr.pixels()[lo:hi]
        pixels = cooler.annotate(
            pixels, 
            bins[['chrom', 'start', 'end', 'weight']], 
            replace=False)
        pixels = pixels[pixels['chrom1'] == pixels['chrom2']].copy()
        pixels['diag'] = pixels['bin2_id'] - pixels['bin1_id']
        pixels['balanced'] = pixels['count'] * pixels['weight1'] * pixels['weight2']
        
        # groupby support regions
        for i, region in enumerate(supports):
            if len(region) == 5:
                sel = (
                      (pixels.chrom1 == region[0])
                    & (pixels.chrom2 == region[0])
                    & (pixels.end1 >= region[1])
                    & (pixels.start1 < region1[2])
                    & (pixels.end2 >= region2[3])
                    & (pixels.start2 < region2[4])
                )
            elif len(region) == 3:
                sel = (
                      (pixels.chrom1 == region[0])
                    & (pixels.chrom2 == region[0])
                    & (pixels.end1 >= region[1])
                    & (pixels.start1 < region[2])
                )
            else:
                raise ValueError(region)
            pixels.loc[sel, 'support'] = i
        pixel_groups = dict(iter(pixels.groupby('support')))
        
        # aggregate
        return {support: pixel_group.groupby('diag')['balanced'].sum()
                      for support, pixel_group in pixel_groups.items()}

    
    supports, support_strs = normalize_supports(clr, supports)
    dtables = make_diag_tables(clr, supports)
    for dt in dtables.values():
        dt['balanced.sum'] = 0
    
    bins = clr.bins()[:]
    spans = partition(0, len(clr.pixels()), chunksize)
    job = partial(process_chunk, clr, supports)
    results = map(job, spans)
    for result in results:
        for i, agg in result.items():
            dt = dtables[i]
            dt['balanced.sum'] = dt['balanced.sum'].add(agg)
    
    for dt in dtables.values():
        dt.iloc[:ignore_diags, dt.columns.get_loc('balanced.sum')] = np.nan
    
    out = pd.concat(
        [dtables[i] for i in range(len(supports))], 
        keys=support_strs, 
        names=['support'])
    return out


def trans_expected(clr, chromosomes, chunksize=1000000, map=map):
    """
    Aggregate the signal in intrachromosomal blocks.
    Can be used as abackground for contact frequencies between chromosomes.

    Parameters
    ----------
    clr : cooler.Cooler
        Cooler object
    chromosomes : list of str
        List of chromosome names
    chunksize : int, optional
        Size of dask chunks
    use_dask : bool, optional
        option to use dask
    
    Returns
    -------
    pandas.DataFrame that stores total number of
    interactions between a pair of chromosomes: 'balanced.sum',
    corresponding number of bins involved
    in the inter-chromosomal interactions: 'n_valid', 
    and a ratio 'balanced.avg = balanced.sum/n_valid', that is
    the actual value of expected for every interchromosomal pair.

    """
    def n_total_trans_elements(clr, chromosomes):
        n = len(chromosomes)
        n_total = [clr.extent(chrom)[1] - clr.extent(chrom)[0] 
                 for chrom in chromosomes]
        pairblock_list = []
        for i in range(n):
            for j in range(i + 1, n):
                # appending to the list of tuples
                pairblock_list.append((chromosomes[i],
                                       chromosomes[j],
                                       n_total[i] * n_total[j] ))
        return pd.DataFrame(pairblock_list, 
            columns=['chrom1', 'chrom2', 'n_total'])

    def n_bad_trans_elements(clr, chromosomes):
        n = 0
        # bad bins are ones with
        # the weight vector being NaN:
        n_bad = [np.sum(clr.bins()['weight']
                       .fetch(chrom)
                       .isnull()
                       .astype(int)
                       .values)
                 for chrom in chromosomes]
        pairblock_list = []
        for i in range(len(n_bad)):
            for j in range(i + 1, len(n_bad)):
                # appending to the list of tuples
                pairblock_list.append((chromosomes[i],
                                       chromosomes[j],
                                       n_bad[i] * n_bad[j] ))
        return pd.DataFrame(pairblock_list,
            columns=['chrom1', 'chrom2', 'n_bad'])

    def process_chunk(clr, span):
        lo, hi = span
        pixels = clr.pixels()[lo:hi]
        # getting pixels that belong to trans-area,
        # defined by the list of chromosomes:
        pixels = cooler.annotate(pixels, clr.bins()[['chrom']], replace=False)
        pixels = pixels[
            (pixels.chrom1.isin(chromosomes)) &
            (pixels.chrom2.isin(chromosomes)) &
            (pixels.chrom1 != pixels.chrom2)
        ]
        pixels['balanced'] = pixels['count'] * pixels['weight1'] * pixels['weight2']
        trans_sum = pixels.groupby(('chrom1', 'chrom2'))['balanced'].sum()
        trans_sum.name = trans_sum.name + '.sum'
        # returning a DataFrame with MultiIndex, that stores
        # pairs of 'balanced.sum' and 'n_valid' values for each
        # pair of chromosomes.
        return trans_sum

    # initialize table
    ntot = n_total_trans_elements(clr, chromosomes).set_index(('chrom1', 'chrom2'))
    nbad = n_bad_trans_elements(clr, chromosomes).set_index(('chrom1', 'chrom2'))
    trans_area = ntot - nbad
    trans_area.name = 'n_valid'
    table = trans_area.to_frame()
    table['balanced.sum'] = 0

    # aggregate trans data
    spans = partition(0, len(clr.pixels()), chunksize)
    job = partial(process_chunk, clr)
    results = map(job, spans)
    for result in results:
        table['balanced.sum'] = table['balanced.sum'].add(result)
    table['balanced.avg'] = table['balanced.sum'] / dtable['n_valid']
    return table



def marginalize():
    # all, cis, trans
    pass
