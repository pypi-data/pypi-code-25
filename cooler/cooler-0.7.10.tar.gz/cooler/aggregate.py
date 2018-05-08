

def joinmerge_coolers(cool_uri, coolers, maxbuf, chrom_subset=None, how='inner', **kwargs):
    # 1. check compatibility
    #  * any common scaffolds on bin tables should be identical.
    #  * warn if no scaffold common to all coolers (maybe you are merging chromosomes!).
    from cooler.tools import partition
    from cooler.io import create_from_unsorted
    
    # normalize the joined bin table
    if usechroms is not None:
        pass
    bins = _join_bin_tables([c.bins()[:] for c in coolers], how=how)
    
    ipixels = (c.pixels()[lo:hi]
                  for lo, hi in partition(0, len(c.pixels()), bufsize)
                       for c in coolers)
    ipixels = map(sanitize_pixels, ipixels)
    create_from_unsorted(cool_uri, bins, ipixels, **kwargs)


def redefine_bins(clr, new_bins):
    """
    sanity checks
     * any common scaffolds on old and new bin table should be identical.
     * there should be at least one common scaffold.
    
    """
    _sanity_check(clr, new_bins)
    
    ipixels = (clr.pixels(join=True)[lo:hi]
                  for lo, hi in partition(0, len(clr.pixels()), bufsize))
    ipixels = map(sanitize_pixels, ipixels)
    create_from_unsorted(cool_uri, new_bins, ipixels, **kwargs)



from pandas.api.types import is_categorical, is_integer
from cooler._writer import CHROM_DTYPE, CHROMID_DTYPE

def rename_scaffolds(clr, scaffolds, h5opts=None):
    if h5opts is None:
        h5opts = dict(compression='gzip', compression_opts=6)
    
    with clr.open('r+') as h5:
        chroms = cooler.core.get(h5['chroms']).set_index('name')
        n_chroms = len(chroms)
        new_names = np.array(chroms.rename(scaffolds).index.values, 
                             dtype=CHROM_DTYPE)  # auto-adjusts char length
        
        del h5['chroms/name']
        h5['chroms'].create_dataset('name',
                           shape=(n_chroms,),
                           dtype=new_names.dtype,
                           data=new_names,
                           **h5opts)
        
        bins = cooler.core.get(h5['bins'])
        n_bins = len(bins)
        idmap = dict(zip(new_names, range(n_chroms)))
        if is_categorical(bins['chrom']) or is_integer(bins['chrom']):            
            chrom_ids = bins['chrom'].cat.codes
            chrom_dtype = h5py.special_dtype(enum=(CHROMID_DTYPE, idmap))
            del h5['bins/chrom']
            try:
                chrom_dset = h5['bins'].create_dataset('chrom',
                                   shape=(n_bins,),
                                   dtype=chrom_dtype,
                                   data=chrom_ids,
                                   **h5opts)
            except ValueError:
                # If HDF5 enum header would be too large, 
                # try storing chrom IDs as raw int instead
                chrom_dtype = CHROMID_DTYPE
                chrom_dset = h5['bins'].create_dataset('chrom',
                                   shape=(n_bins,),
                                   dtype=chrom_dtype,
                                   data=chrom_ids,
                                   **h5opts)


#groupby_scatter
def scatter_blocks(clr, chunksize, tmp):
    spans = cooler.tools.partition(0, len(clr.pixels()), chunksize)
    created = set()
    output = {}
    for i, (lo, hi) in enumerate(spans):
        print('chunk {}'.format(i), flush=True)
        
        chunk = clr.pixels()[lo:hi]
        chunk = cooler.annotate(chunk, clr.bins()[['chrom']], replace=False)
        grouped = chunk.groupby(['chrom1', 'chrom2'])
        
        for (chrom1, chrom2), group in grouped:
            outname = '{}_{}'.format(chrom1, chrom2)
            
            if (chrom1, chrom2) not in created:
                print('creating', outname, flush=True)
                cooler.io.create(
                    tmp + '::' + outname,
                    clr.bin()[:],
                    group,
                    append=True
                )
                output[chrom1, chrom2] = group
                created.add((chrom1, chrom2))
            else:
                print('appending to', outname, flush=True)
                cooler.io.append(
                    tmp + '::' + outname,
                    'pixels',
                    group,
                )  
                output[chrom1, chrom2] = pd.concat([output[chrom1, chrom2], group], ignore_index=True)
    return output
