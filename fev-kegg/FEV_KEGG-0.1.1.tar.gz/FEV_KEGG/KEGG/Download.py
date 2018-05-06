from builtins import int
import urllib

from FEV_KEGG.lib.Biopython.KEGG import REST
from bs4 import BeautifulSoup
from retrying import retry
import tqdm
from typing import List

from FEV_KEGG.Util import Util, Parallelism
from FEV_KEGG.KEGG import SSDB
import FEV_KEGG.settings as settings
import concurrent.futures


def is_not_404(exception):
    return not ( isinstance(exception, urllib.error.HTTPError) and exception.code == 404 )


@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax, retry_on_exception=is_not_404)
def downloadPathwayList(organismString: 'eg. eco'):
    """
    downloads list of all pathways for a given organism from KEGG
    """
    return REST.kegg_list('pathway', organismString, timeout=settings.downloadTimeoutSocket).read()


@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax, retry_on_exception=is_not_404) # do not retry on HTTP error 404, raise immediately instead
def downloadPathway(organismString: 'eg. eco', pathwayName: 'eg. 00260'):
    """
    downloads pathway as KGML for a given organism from KEGG
    """
    return REST.kegg_get(organismString + pathwayName, 'kgml', timeout=settings.downloadTimeoutSocket).read()
    

@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax)
def downloadGene(geneID: 'string eco:b0004'):
    """
    downloads gene description for a given gene ID (includes organism) from KEGG
    """
    result = REST.kegg_get(geneID, timeout=settings.downloadTimeoutSocket).read()
    if len( result ) < 3:
        raise IOError( "Download too small:\n" + result)
    else:
        return result

def downloadGeneBulk(geneIDs: 'list of strings [eco:b0004, eco:b0015,...]'):
    """
    downloads gene descriptions for a given list of gene IDs (includes organism) from KEGG
    """    
    max_query_count = 10 # hard limit imposed by KEGG server
    
    # split list of GeneIDs into chunks of size max_query_count
    geneIDs_chunks = Util.chunks(geneIDs, max_query_count)
    
    # form sub-queries
    query_parts = []
    for chunk in geneIDs_chunks:
        query_parts.append( '+'.join(chunk) )
    
    tqdmPosition = Parallelism.getTqdmPosition()
    threadPool = concurrent.futures.ThreadPoolExecutor(Parallelism.getNumberOfThreadsDownload())
    futures = []
    iterator = None
    
    try:
        # query KEGG in parallel
        
        for query_part in query_parts:
            futures.append( threadPool.submit(_downloadGeneBulk, query_part) )
        
        iterator = concurrent.futures.as_completed(futures)
        
        if settings.verbosity >= 1:
            if settings.verbosity >= 2:
                print( 'Downloading ' + str(len(geneIDs)) + ' genes, max. ' + str(max_query_count) + ' per chunk...' )
            iterator = tqdm.tqdm(iterator, total = len(query_parts), unit = ' *10 genes', position = tqdmPosition)
        
        result = ''
        for future in iterator:
            try:
                result_part = future.result()
            except concurrent.futures.CancelledError:
                continue
            result += result_part
            
        threadPool.shutdown(wait = False)
    
    except KeyboardInterrupt: # only raised in main thread (once in each process!)
        
        Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, terminateProcess=True)
        raise
    
    except BaseException:
        
        if Parallelism.isMainThread():
            Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, silent=True)
        raise
        
    finally:
        
        if iterator is not None: iterator.close()
    
    return result

@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax)
def _downloadGeneBulk(query_part):
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    else:
        result = REST.kegg_get(query_part, timeout=settings.downloadTimeoutSocket).read()
        if len( result ) < 3:
            raise IOError( "Download too small:\n" + result)
        else:
            return result


@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax)
def downloadOrganismList():
    """
    download the list of all organisms known to KEGG.
    """
    return REST.kegg_list('organism', timeout=settings.downloadTimeoutSocket).read()


@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax, retry_on_exception=is_not_404) # do not retry on HTTP error 404, raise immediately instead
def downloadEnzymeEcNumbers(enzymeAbbreviation):
    """
    download the list of enzyme EC numbers from KEGG.
    """
    paralog_ecNumbers = []
    
    # look up enzyme EC numbers
    searchResult = REST.kegg_find('enzyme', enzymeAbbreviation, timeout=settings.downloadTimeoutSocket).read().split('\n')
    for line in searchResult:
        
        if len( line ) < 10:
            continue
        
        ecNumber = line.split('\t')[0].split(':')[1]
        paralog_ecNumbers.append(ecNumber)
    
    return '\n'.join(paralog_ecNumbers)


@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax, retry_on_exception=is_not_404) # do not retry on HTTP error 404, raise immediately instead
def doesOrganismExistDownload(organismAbbreviation):
    """
    Downloads the info file of an organism.
    Returns True if something was downloaded, and thus the organism exists.
    Returns False if download was empty (400 Bad Request), because this organism does not exist.
    """
    organismInfo = downloadOrganismInfo(organismAbbreviation)
    if organismInfo is None:
        return False
    else:
        return True


@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax, retry_on_exception=is_not_404) # do not retry on HTTP error 404, raise immediately instead
def downloadOrganismInfo(organismAbbreviation):
    """
    Downloads the info file of an organism.
    Returns True if something was downloaded, and thus the organism exists.
    Returns False if download was empty (400 Bad Request), because this organism does not exist.
    """
    try:
        return REST.kegg_info(organismAbbreviation, timeout=settings.downloadTimeoutSocket).read()
    except urllib.error.HTTPError as e:
        if isinstance(e, urllib.error.HTTPError) and e.code == 400:
            return None
        else:
            raise




def downloadOrthologs(geneID: 'GeneID', comparisonOrganismString: 'eco') -> List[SSDB.PreMatch]:
    """
    download GeneID strings for orthologs of gene 'geneIdString' found in organism 'comparisonOrganismString'.
    """
    # download list of orthologs
    data = _downloadHomologs(geneID.geneIDString, comparisonOrganismString)
    
    # parse HTML
    foundGenes = _parseSsdbOrthologView(data)
    
    return foundGenes   
    

def downloadParalogs(geneID: 'GeneID') -> List[SSDB.PreMatch]:
    """
    download GeneID strings for paralogs of gene 'geneIdString'.
    """
    # download list of paralogs
    data = _downloadHomologs(geneID.geneIDString, geneID.organismAbbreviation)
    
    # parse HTML
    foundGenes = _parseSsdbOrthologView(data)
    
    # remove the gene that was searched for
    for preMatch in foundGenes:
        if preMatch.foundGeneIdString == geneID.geneIDString:
            foundGenes.remove(preMatch)
            break
    
    return foundGenes

@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax, retry_on_exception=is_not_404) # do not retry on HTTP error 404, raise immediately instead
def _downloadHomologs(geneIdString, organismAbbreviationString):
    return str(urllib.request.urlopen('http://www.kegg.jp/ssdb-bin/ssdb_ortholog_view?org_gene=' + geneIdString + '&org=' + organismAbbreviationString, timeout=settings.downloadTimeoutSocket).read()).replace('\\n', '')

def _parseSsdbOrthologView(htmlString) -> List[SSDB.PreMatch]:
    
    html = BeautifulSoup(htmlString, 'html.parser')
    
    matches = []
    
    for index, tr in enumerate( html.table.children ):
        
        # ignore head of table
        if index == 0:
            continue
        
        for index, td in enumerate( tr.children ):
             
            if index == 0: # read gene ID
                foundGeneIdString = td.text
                 
            elif index == 1: # read Smith-Waterman score
                swScore = int(td.text)
                 
            elif index == 2: # read bit score
                bitScore = float(td.text)
                 
            elif index == 3: # read identity
                identity = float(td.text)
                 
            elif index == 4: # read overlap
                overlap = int(td.text)
        
        matches.append( SSDB.PreMatch(foundGeneIdString, swScore, bitScore, identity, overlap) )
    
    return matches







@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax)
def downloadTaxonomyNCBI():
    return REST.kegg_get('br:br08610', timeout=settings.downloadTimeoutSocket).read()


@retry(wait_exponential_multiplier=settings.retryDownloadBackoffFactor, wait_exponential_max=settings.retryDownloadBackoffMax, stop_max_delay=settings.retryDownloadMax)
def downloadTaxonomyKEGG():
    return REST.kegg_get('br:br08601', timeout=settings.downloadTimeoutSocket).read()

    