import re
import time
import urllib

from FEV_KEGG.lib.Biopython.KEGG.KGML import KGML_pathway, KGML_parser
import jsonpickle
from FEV_KEGG.KEGG.GENE import Gene
import tqdm
from typing import Set, List, Dict, Iterable, Tuple

from FEV_KEGG.Graph.Elements import GeneID
from FEV_KEGG.KEGG import File, Download, SSDB
import FEV_KEGG.settings as settings
from FEV_KEGG.Util import Parallelism
import concurrent.futures


class NoKnownPathwaysError(ValueError):
    """
    Raised if an organism has no known pathways and is therefore rather useless.
    """
    pass

class ImpossiblyOrthologousError(ValueError):
    """
    Raised if trying to find orthologs in an Organism using a GeneID from the very same Organism.
    """

def getPathwayDescriptions(organismString: 'eco') -> Set[str]:
    """
    returns the list of pathways for given organism. Downloads the data from KEGG, if not already present on disk.
    """
    
    fileName = 'organism/' + organismString + '/pathway/list'
    
    debugOutput = 'Getting pathway list for ' + organismString + ' from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
            
        pathwayList = File.readSetFromFileAtOnce(fileName)
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        try:
            pathwayList = Download.downloadPathwayList(organismString)
        except urllib.error.HTTPError as exception:
            if isinstance(exception, urllib.error.HTTPError) and exception.code == 404: # organism has no known pathways
                raise NoKnownPathwaysError('The organism \'' + organismString + '\' has no known pathways.')
            else:
                raise
        File.writeToFile(pathwayList, fileName)
        
    return pathwayList
    
    
def getPathway(organismString: 'eco', pathwayName: '00260') -> KGML_pathway.Pathway:
    """
    returns a Bio.KEGG.KGML.KGML_pathway.Pathway for given organism. Downloads the data from KEGG, if not already present on disk.
    """
    
    fileName = 'organism/' + organismString + '/pathway/' + pathwayName
    
    debugOutput = 'Getting pathway ' + pathwayName + ' for ' + organismString + ' from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
            
        fileHandle = File.getFileHandleRead(fileName)
        pathway = KGML_parser.read(fileHandle)
        
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        try: # certain pathways might not exist as KGML (HTTP error 404), ignore these and return None
            pathwayXml = Download.downloadPathway(organismString, pathwayName)
        except urllib.error.HTTPError as exception:
            if isinstance(exception, urllib.error.HTTPError) and exception.code == 404:
                return None
            else:
                raise
            
        File.writeToFile(pathwayXml, fileName)
        pathway = KGML_parser.read(pathwayXml)
    
    return pathway

def getPathwayBulk(organismString: 'eco', pathwayNames: List[str]) -> Dict[str, KGML_pathway.Pathway]:
    """
    returns a list of Bio.KEGG.KGML.KGML_pathway.Pathway for given organism. Downloads the data from KEGG in bulk, if not already present on disk.
    """
    
    # split list into pathways on disk and pathways not downloaded yet
    pathwaysOnDisk = []
    pathwaysToDownload = []
    
    for pathwayName in pathwayNames:
        
        fileName = 'organism/' + organismString + '/pathway/' + pathwayName
        
        debugOutput = 'Getting pathway ' + pathwayName + ' from '
        
        if File.doesFileExist(fileName):
        
            if settings.verbosity >= 2:
                print(debugOutput + 'disk.')
            
            pathwaysOnDisk.append(pathwayName)
        
        else:
            if settings.verbosity >= 2:
                print(debugOutput + 'download.')
            
            pathwaysToDownload.append(pathwayName)
    
    
    pathways = dict()
    # get pathways from disk
    for pathwayName in pathwaysOnDisk:
        
        fileName = 'organism/' + organismString + '/pathway/' + pathwayName
        
        fileHandle = File.getFileHandleRead(fileName)
        pathway = KGML_parser.read(fileHandle)
        pathways[pathwayName] = pathway
    
    
    # download pathways in bulk
    if len( pathwaysToDownload ) > 0:
        tqdmPosition = Parallelism.getTqdmPosition()
        threadPool = concurrent.futures.ThreadPoolExecutor(Parallelism.getNumberOfThreadsDownload())
        futures = []
        iterator = None
        
        try:
            # query KEGG in parallel
            
            for pathwayToDownload in pathwaysToDownload:
                futures.append( threadPool.submit(_downloadPathway, pathwayToDownload, organismString) )
            
            iterator = concurrent.futures.as_completed(futures)
            
            if settings.verbosity >= 1:
                if settings.verbosity >= 2:
                    print( 'Downloading ' + str(len(pathwaysToDownload)) + ' pathways...' )
                iterator = tqdm.tqdm(iterator, total = len(pathwaysToDownload), unit = ' pathways', position = tqdmPosition)
                
            for future in iterator:
                
                result_part = future.result()
                if result_part is not None:
                    pathway = KGML_parser.read(result_part)
                    pathwayName = re.sub('[^0-9]', '', pathway.name)
                    pathways[pathwayName] = pathway
                    
                    fileName = 'organism/' + organismString + '/pathway/' + pathwayName
                    File.writeToFile(result_part, fileName)
            
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

    return pathways


def _downloadPathway(pathwayName, organismString):
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    else:
        try: # certain pathways might not exist as KGML (HTTP error 404), ignore these and return None
            pathwayXml = Download.downloadPathway(organismString, pathwayName)
        except urllib.error.HTTPError as exception:
            if isinstance(exception, urllib.error.HTTPError) and exception.code == 404:
                return None
            else:
                raise
        return pathwayXml







def getGene(geneIdString: 'eco:b0004') -> Gene:
    """
    returns a Gene for given gene ID. Downloads the data from KEGG, if not already present on disk.
    """
    organismString, geneString = geneIdString.split(':')
    fileName = 'organism/' + organismString + '/gene/' + geneString
    
    debugOutput = 'Getting gene ' + geneIdString + ' from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity >= 2:
            print(debugOutput + 'disk.')
        
        fileContent = File.readStringFromFileAtOnce(fileName)
        gene = Gene(fileContent)

    else:
        if settings.verbosity >= 2:
            print(debugOutput + 'download.')
        
        geneText = Download.downloadGene(geneIdString)
        File.writeToFile(geneText, fileName)
        gene = Gene(geneText)

    return gene


def getGeneBulk(geneIDs: Iterable[GeneID]) -> Dict[GeneID, Gene]:
    """
    returns a list of Gene for every given gene ID. Downloads the data from KEGG in bulk, if not already present on disk.
    """
    # split list into genes on disk and genes not downloaded yet
    genesOnDisk = []
    genesToDownload = []
    
    for geneID in geneIDs:
        organismString = geneID.organismAbbreviation
        geneString = geneID.geneName
        fileName = 'organism/' + organismString + '/gene/' + geneString
        
        debugOutput = 'Getting gene ' + str( geneID ) + ' from '
        
        if File.doesFileExist(fileName):
        
            if settings.verbosity >= 2:
                print(debugOutput + 'disk.')
            
            genesOnDisk.append(geneID)
        
        else:
            if settings.verbosity >= 2:
                print(debugOutput + 'download.')
            
            genesToDownload.append(geneID)
    
    
    # get genes from disk
    geneEntries = dict()
    for geneID in genesOnDisk:
        
        organismString = geneID.organismAbbreviation
        geneString = geneID.geneName
        fileName = 'organism/' + organismString + '/gene/' + geneString
        
        fileContent = File.readStringFromFileAtOnce(fileName)
        gene = Gene(fileContent)
        geneEntries[geneID] = gene
    
    
    # download genes in bulk
    if len( genesToDownload ) > 0:
        geneTextBulk = Download.downloadGeneBulk([x.__str__() for x in genesToDownload])
        geneTexts = re.split('///\n', geneTextBulk)[:-1]
        for geneText in geneTexts:
            
            geneText += '///'
            
            gene = Gene(geneText)
            
            organismString = gene.organismAbbreviation
            geneString = gene.number
            
            geneEntries[GeneID(organismString + ':' + geneString)] = gene
            
            fileName = 'organism/' + organismString + '/gene/' + geneString
            File.writeToFile(geneText, fileName)

    return geneEntries



def getPathwayGeneIDs(organismString: 'eco', pathwayName: '00260') -> Set[str]:
    """
    returns the set of gene ID strings from a pathway, or None, if not on disk.
    """
    fileName = 'organism/' + organismString + '/pathway/' + pathwayName + '_geneID_list'
    
    debugOutput = 'Getting gene ID list for pathway ' + organismString + pathwayName + ' from '
        
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
        return File.readSetFromFileAtOnce(fileName)
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'calculation.')
        return None


def setPathwayGeneIDs(organismString: 'eco', pathwayName: '00260', geneIDs: Set[str]):
    """
    saves the set of gene IDs to disk.
    """
    fileName = 'organism/' + organismString + '/pathway/' + pathwayName + '_geneID_list'
    geneIDListString = '\n'.join(geneIDs)
    
    File.writeToFile(geneIDListString, fileName)
    

def getOrganismList() -> List[str]:
    """
    Returns the list of all known organisms from KEGG.
    """
    fileName = 'organism_list'
    
    debugOutput = 'Getting organism list from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
        organismList = File.readListFromFileAtOnce(fileName)
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        organismList = Download.downloadOrganismList()
        File.writeToFile(organismList, fileName)
        organismList = organismList.splitlines()

    return organismList


def getEnzymeEcNumbers(enzymeAbbreviation: 'MiaB') -> List[str]:
    """
    Returns the list of all EC numbers for a given enzyme, identified by its abbreviation, from KEGG.
    Also works for everything else in the description of an enzyme, not just the abbreviation.
    """
    fileName = 'enzymes/' + enzymeAbbreviation
    
    debugOutput = 'Getting enzyme EC number list for' + enzymeAbbreviation + ' from '
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
        ecNumbers = File.readListFromFileAtOnce(fileName)
        
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        ecNumbers = Download.downloadEnzymeEcNumbers(enzymeAbbreviation)
        File.writeToFile(ecNumbers, fileName)
        ecNumbers = ecNumbers.splitlines()

    return ecNumbers


def doesOrganismExist(organismString: 'eco') -> bool:
    """
    Returns True if something was downloaded, and thus the organism exists.
    Returns False if download was empty (400 Bad Request), because this organism does not exist.
    """
    folderName = 'organism/' + organismString + '/'
    
    debugOutput = 'Getting organism folder ' + organismString + ' from '
    
    if File.doesFolderExist(folderName):
        
        if settings.verbosity >= 2:
            print(debugOutput + 'disk.')
        return True            
    
    else:
        if settings.verbosity >= 2:
            print(debugOutput + 'download.')
        
        organismExists = Download.doesOrganismExistDownload(organismString)
        
        if organismExists is True:
            
            File.createPath(folderName)
            return True
        
        else:
            
            return False
        
def _doesOrganismExistTuple(organismString: 'eco') -> Tuple[str, bool]:
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    else:
        return (organismString, doesOrganismExist(organismString))

def doesOrganismExistBulk(organismStrings: List[str]) -> List[str]:
    """
    Returns a list of organism abbreviations, taken from 'organismStrings' for which doesOrganismExist() would return True.
    """
    tqdmPosition = Parallelism.getTqdmPosition()
    threadPool = concurrent.futures.ThreadPoolExecutor(Parallelism.getNumberOfThreadsDownload())
    futures = []
    iterator = None
    
    try:
        for organismString in organismStrings:
            futures.append( threadPool.submit(_doesOrganismExistTuple, organismString) )
        
        iterator = concurrent.futures.as_completed(futures)
        
        if settings.verbosity >= 1:
#             if settings.verbosity >= 2:
            print( 'Checking existance of ' + str(len(organismStrings)) + ' organisms...' )
            iterator = tqdm.tqdm(iterator, total = len(organismStrings), unit = ' organisms', position = tqdmPosition)
        
        existingOrganisms = []
    
        for future in iterator:
            
            doesExistTuple = future.result()
            organismString, doesExist = doesExistTuple
            if doesExist is True:
                existingOrganisms.append(organismString)
            else:
                raise ValueError('Organism abbreviation does not exist: ' + organismString)
        
        threadPool.shutdown(wait = False)
        
        return existingOrganisms
    
    except KeyboardInterrupt: # only raised in main thread (once in each process!)
        
        Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, terminateProcess=True)
        raise
    
    except BaseException:
        
        if Parallelism.isMainThread():
            Parallelism.keyboardInterruptHandler(threadPool=threadPool, threadPoolFutures=futures, silent=True)
        raise
        
    finally:
        
        if iterator is not None: iterator.close()
            
        



def getOrthologsOnlyGeneID(geneID: GeneID, comparisonOrganism: 'Organism', eValue: float = 1e-15) -> Set[GeneID]:
    """
    Returns the list of orthologs for gene 'geneID' in organism 'comparisonOrganism'.
    Only genes with an E-value smaller or equal to 'eValue' are returned.
    Orthologs are downloaded from KEGG SSDB.
    """
    
    return _filterHomologsBySignificance( _getHomologs(geneID, comparisonOrganism.nameAbbreviation), eValue, onlyGeneID = True)

def getOrthologs(geneID: GeneID, comparisonOrganism: 'Organism', eValue: float = 1e-15) -> SSDB.Matching:
    """
    Returns a Matching of orthologs for gene 'geneID', searching the genome of 'comparisonOrganism'.
    
    Only matches with an E-value smaller or equal to 'eValue' are returned.
    Matches are downloaded from KEGG SSDB.
    
    Raises ImpossiblyOrthologousError if 'geneID' is from 'comparisonOrganism'.
    """
       
    return _filterHomologsBySignificance( _getHomologs(geneID, comparisonOrganism.nameAbbreviation), eValue, onlyGeneID = False)
    

def getParalogsOnlyGeneID(geneID: GeneID, eValue: float = 1e-15) -> Set['GeneID']:
    """
    Returns the list of paralogs for gene 'geneID'.
    Only genes with an E-value smaller or equal to 'eValue' are returned.
    Paralogs are downloaded from KEGG SSDB.
    """
           
    return _filterHomologsBySignificance( _getHomologs(geneID, comparisonOrganismString = None), eValue, onlyGeneID = True)

def getParalogs(geneID: GeneID, eValue: float = 1e-15) -> SSDB.Matching:
    """
    Returns a Matching of paralogs for gene 'geneID'.
    
    Only matches with an E-value smaller or equal to 'eValue' are returned.
    Matches are downloaded from KEGG SSDB.
    """
           
    return _filterHomologsBySignificance( _getHomologs(geneID, comparisonOrganismString = None), eValue, onlyGeneID = False)

def _getHomologs(geneID: GeneID, comparisonOrganismString = None) -> SSDB.Matching:
    
    if comparisonOrganismString is None: # looking for paralogs
        fileName = 'organism/' + geneID.organismAbbreviation + '/paralogs/' + geneID.geneName
        debugOutput = 'Getting paralogs for ' + geneID.geneIDString + ' from '
    
    else: # looking for orthologs
        if geneID.organismAbbreviation == comparisonOrganismString:
            raise ImpossiblyOrthologousError('GeneID is from the same Organism I ought to search in. This can never be an ortholog!')
        fileName = 'organism/' + geneID.organismAbbreviation + '/orthologs/' + geneID.geneName + '/' + comparisonOrganismString
        debugOutput = 'Getting orthologs for ' + geneID.geneIDString + ' in ' + comparisonOrganismString + ' from '
    
    
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        # looking for paralog or ortholog?
        if comparisonOrganismString is None: # looking for paralogs
            
            preMatches = Download.downloadParalogs(geneID)
            databaseOrganism = geneID.organismAbbreviation
            
        else: # looking for orthologs
            
            preMatches = Download.downloadOrthologs(geneID, comparisonOrganismString)
            databaseOrganism = comparisonOrganismString
        
        # get length of query sequence
        queryGene = getGene(geneID.geneIDString)
        searchSequenceLength = queryGene.aaseqLength
        
        # add size of database
        organismInfo = Download.downloadOrganismInfo(databaseOrganism)
        organismGeneEntries = int( re.split('([0-9,]+) entries', organismInfo)[1].replace(',', '') )
        
        # add lengths of result sequences
        matches = []
        for preMatch in preMatches:
            
            # length
            matchedGene = getGene(preMatch.foundGeneIdString)
            sequenceLength = matchedGene.aaseqLength
            
            matches.append( SSDB.Match.fromPreMatch(preMatch, sequenceLength))

        timestamp = int( time.time() )
        
        # create Matching
        matching = SSDB.Matching(geneID, searchSequenceLength, databaseOrganism, organismGeneEntries, matches, timestamp)
        
        # save to file
        jsonpickle.set_encoder_options('simplejson', indent=4)
        File.writeToFile(jsonpickle.encode(matching), fileName)
        
    fileContent = File.readStringFromFileAtOnce(fileName)
    
    matching = jsonpickle.decode(fileContent)
    
    return matching

def _filterHomologsBySignificance(matching: SSDB.Matching, eValue, onlyGeneID = False):
    return _filterHomologsBySignificanceBulk({'0': matching}, eValue, onlyGeneID).get('0')


def getOrthologsBulk(geneIDs: Iterable[GeneID], comparisonOrganism: 'Organism', eValue: float = 1e-15) -> Dict[GeneID, SSDB.Matching]:
    """
    Returns a Matching of orthologs for each gene in 'geneIDs'.
     
    Only matches with an E-value smaller or equal to 'eValue' are returned.
    Matches are downloaded in parallel from KEGG SSDB.
    """
            
    return _filterHomologsBySignificanceBulk( _getHomologsBulk(geneIDs, comparisonOrganism.nameAbbreviation), eValue, onlyGeneID = False)

def getParalogsBulk(geneIDs: Iterable[GeneID], eValue: float = 1e-15) -> Dict[GeneID, SSDB.Matching]:
    """
    Returns a Matching of paralogs for each gene in 'geneIDs'.
     
    Only matches with an E-value smaller or equal to 'eValue' are returned.
    Matches are downloaded in parallel from KEGG SSDB.
    """
            
    return _filterHomologsBySignificanceBulk( _getHomologsBulk(geneIDs, comparisonOrganismString = None), eValue, onlyGeneID = False)

def _getHomologsBulk(geneIDs: Iterable[GeneID], comparisonOrganismString = None) -> Dict[GeneID, SSDB.Matching]:
    
    # split list into matchings on disk and matchings not downloaded yet
    matchingsOnDisk = []
    matchingsToDownload = []
    
    for geneID in geneIDs:
        
        if comparisonOrganismString is None: # looking for paralogs
            fileName = 'organism/' + geneID.organismAbbreviation + '/paralogs/' + geneID.geneName
            debugOutput = 'Getting paralogs for ' + geneID.geneIDString + ' from '
        
        else: # looking for orthologs
            if geneID.organismAbbreviation == comparisonOrganismString:
                raise ImpossiblyOrthologousError('GeneID is from the same Organism I ought to search in. This can never be an ortholog!')
            fileName = 'organism/' + geneID.organismAbbreviation + '/orthologs/' + geneID.geneName + '/' + comparisonOrganismString
            debugOutput = 'Getting orthologs for ' + geneID.geneIDString + ' in ' + comparisonOrganismString + ' from '
        
        
        if File.doesFileExist(fileName):
            
            if settings.verbosity > 1:
                print(debugOutput + 'disk.')
                
            matchingsOnDisk.append(geneID)
        
        else:
            if settings.verbosity > 1:
                print(debugOutput + 'download.')
            
            matchingsToDownload.append(geneID)
    
    
    # get matchings from disk
    matchings = dict()
    for geneID in matchingsOnDisk:
        
        if comparisonOrganismString is None: # looking for paralogs
            fileName = 'organism/' + geneID.organismAbbreviation + '/paralogs/' + geneID.geneName
        
        else: # looking for orthologs
            fileName = 'organism/' + geneID.organismAbbreviation + '/orthologs/' + geneID.geneName + '/' + comparisonOrganismString

        fileContent = File.readStringFromFileAtOnce(fileName)
        matching = jsonpickle.decode(fileContent, classes=SSDB.Matching)
        matchings[geneID] = matching
    
    # download matchings in bulk
    if len( matchingsToDownload ) > 0:
        
        tqdmPosition = Parallelism.getTqdmPosition()
        threadPool = concurrent.futures.ThreadPoolExecutor(Parallelism.getNumberOfThreadsDownload())
        futures = []
        iterator = None
        
        try:
            # query KEGG SSDB in parallel
            
            for matchingToDownload in matchingsToDownload:
                futures.append( threadPool.submit(_getHomologsBulkHelper, matchingToDownload, comparisonOrganismString) )
            
            iterator = concurrent.futures.as_completed(futures)
            
            if settings.verbosity >= 1:    
                if settings.verbosity >= 2:
                    print( 'Downloading ' + str(len(matchingsToDownload)) + ' matchings...' )
                iterator = tqdm.tqdm(iterator, total = len(matchingsToDownload), unit = ' matchings', position = tqdmPosition)
            
            for future in iterator:
                matching = future.result()
                matchings[matching.queryGeneID] = matching
            
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
        
    return matchings

def _getHomologsBulkHelper(geneID, comparisonOrganismString) -> SSDB.Matching:
    
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    
    preMatches = _downloadHomolog(geneID, comparisonOrganismString)
    
    if preMatches is None: # may happen if there is no matching in SSDB
        return None
    
    if comparisonOrganismString is None: # looking for paralogs
        fileName = 'organism/' + geneID.organismAbbreviation + '/paralogs/' + geneID.geneName
        databaseOrganism = geneID.organismAbbreviation
        
    else: # looking for orthologs
        fileName = 'organism/' + geneID.organismAbbreviation + '/orthologs/' + geneID.geneName + '/' + comparisonOrganismString
        databaseOrganism = comparisonOrganismString
    
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    
    # get length of query sequence
    queryGene = getGene(geneID.geneIDString)
    searchSequenceLength = queryGene.aaseqLength
    
    if Parallelism.getShallCancelThreads() is True:
        raise concurrent.futures.CancelledError()
    
    # add size of database
    organismInfo = Download.downloadOrganismInfo(databaseOrganism)
    organismGeneEntries = int( re.split('([0-9,]+) entries', organismInfo)[1].replace(',', '') )
    
    # add lengths of result sequences
    matches = []
    for preMatch in preMatches:
        
        if Parallelism.getShallCancelThreads() is True:
            raise concurrent.futures.CancelledError()
        
        # length
        matchedGene = getGene(preMatch.foundGeneIdString)
        sequenceLength = matchedGene.aaseqLength
        
        matches.append( SSDB.Match.fromPreMatch(preMatch, sequenceLength))

    timestamp = int( time.time() )
    
    # create Matching
    matching = SSDB.Matching(geneID, searchSequenceLength, databaseOrganism, organismGeneEntries, matches, timestamp)
    
    # save to file
    jsonpickle.set_encoder_options('simplejson', indent=4)
    File.writeToFile(jsonpickle.encode(matching), fileName)
    
    return matching

def _downloadHomolog(geneID, comparisonOrganismString):
    try:
        if comparisonOrganismString is None: #paralog
            return Download.downloadParalogs(geneID)
        else: #ortholog
            return Download.downloadOrthologs(geneID, comparisonOrganismString)
    except urllib.error.HTTPError as exception:
        if isinstance(exception, urllib.error.HTTPError) and exception.code == 404:
            return None
        else:
            raise
    
    

def _filterHomologsBySignificanceBulk(matchings: Dict[GeneID, SSDB.Matching], eValue, onlyGeneID = False):
    
    result = dict()
    
    for geneID, matching in matchings.items():
        
        if onlyGeneID is True:
            # filter non-significant genes
            geneIDs = set()
            
            for match in matching.matches:
                if match.eValue <= eValue:
                    geneIDs.add( match.foundGeneID )
                
            resultPart = geneIDs
        
        else:
            # filter non-significant genes
            validMatches = []
            
            for match in matching.matches:
                if match.eValue <= eValue:
                    validMatches.append(match)
            matching.matches = validMatches
            
            resultPart = matching
        
        result[geneID] = resultPart
    
    return result
        
    
    
    

def getTaxonomyNCBI() -> List[str]:
    """
    Returns the taxonomy of organisms in KEGG, following the NCBI scheme.
    """
    fileName = 'taxonomy/NCBI_raw'
    debugOutput = 'Getting NCBI taxonomy from '
    return _getTaxonomy(fileName, debugOutput, True)


def getTaxonomyKEGG() -> List[str]:
    """
    Returns the taxonomy of organisms in KEGG, following the KEGG scheme.
    """
    fileName = 'taxonomy/KEGG_raw'
    debugOutput = 'Getting KEGG taxonomy from '
    return _getTaxonomy(fileName, debugOutput, False)
    

def _getTaxonomy(fileName, debugOutput, isNCBI) -> List[str]:
    if File.doesFileExist(fileName):
        
        if settings.verbosity > 1:
            print(debugOutput + 'disk.')
    
    else:
        if settings.verbosity > 1:
            print(debugOutput + 'download.')
        
        if isNCBI:
            organismList = Download.downloadTaxonomyNCBI()
        else:
            organismList = Download.downloadTaxonomyKEGG()
        File.writeToFile(organismList, fileName)
        
    fileContent = File.readListFromFileAtOnce(fileName)

    return fileContent
    