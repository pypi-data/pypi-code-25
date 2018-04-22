from collections import OrderedDict

import mygene

from biopipe.contexts import no_output
from biopipe.decorators import Pipe
from biopipe.transformers import FileReadTransformer
from biopipe.transformers import ListTransformer

HOMO_SAPIENS_SPECIES_ID = 9606
mg = mygene.MyGeneInfo()


def get_first_item(items):
    """Return the first item of items. If 'items' is a single value, just return it."""
    return mygene.alwayslist(items)[0]


@Pipe(pipe_transformer=ListTransformer, argument_transformer=FileReadTransformer(ListTransformer))
def ensg2symbol(ensembl_ids=None):
    """Convert Ensembl gene ids into gene symbols."""
    # Silently query mygene server.
    with no_output():
        query_results = mg.getgenes(ensembl_ids, fields='symbol', species=HOMO_SAPIENS_SPECIES_ID)
    raw_result = [(query_result['query'], query_result['symbol']) for query_result in query_results if 'symbol' in query_result]

    best_result = OrderedDict()
    for query_id, symbol in raw_result:
        if query_id not in best_result:
            best_result[query_id] = symbol

    print('\n'.join(best_result.values()))


@Pipe(pipe_transformer=ListTransformer, argument_transformer=FileReadTransformer(ListTransformer))
def symbol2ensg(symbols=None):
    """Convert gene symbols into Ensembl gene ids."""
    # Silently query mygene server.
    with no_output():
        query_results = mg.querymany(symbols, scopes='symbol', fields='ensembl.gene', species=9606)
    raw_result = [(query_result['query'], get_first_item(query_result['ensembl'])['gene'])
                  for query_result in query_results
                  if 'ensembl' in query_result]

    best_result = OrderedDict()
    for query_symbol, ensembl_id in raw_result:
        if query_symbol not in best_result:
            best_result[query_symbol] = ensembl_id

    print('\n'.join(best_result.values()))
