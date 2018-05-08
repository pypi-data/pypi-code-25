import prefixcommons.curie_util as cu
import pandas as pd

def to_dataframe(prefixes=None, cmaps=None, csvfile=None):
    if prefixes is None:
        prefixes = cu.get_prefixes()

    prefixes.remove("")
    if cmaps is None:
        cmaps = ['monarch_context','obo_context']

    cmap_dict = {}
    for cmap in cmaps:
        cmap_dict[cmap] = cu.read_biocontext(cmap)
    entries = []
    for p in prefixes:
        e= {}
        for cmap in cmaps:
            d = cmap_dict[cmap]
            if p in d:
                e[cmap] = d[p]
        
        entries.append(e)
    df = pd.DataFrame(entries, index=prefixes)
    df.index.name = 'prefix'
    if csvfile is not None:
        df.to_csv(csvfile)
    return df
