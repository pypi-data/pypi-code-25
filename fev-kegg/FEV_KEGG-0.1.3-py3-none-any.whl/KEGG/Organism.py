from builtins import str
import re

from FEV_KEGG.lib.Biopython.KEGG.KGML import KGML_pathway
from FEV_KEGG.KEGG.GENE import Gene
from typing import Set, List, Iterable, Generator

from FEV_KEGG.Graph.SubstrateGraphs import SubstrateEnzymeGraph, SubstrateEcGraph, SubstrateGeneGraph, SubstrateReactionGraph, Conversion
from FEV_KEGG.KEGG import Database
from FEV_KEGG.KEGG.Database import NoKnownPathwaysError
from FEV_KEGG.KEGG.File import cache, cacheEntry
import tqdm
import FEV_KEGG.settings as settings

import concurrent.futures
from FEV_KEGG.Util import Parallelism
import gc
import FEV_KEGG.quirks as quirks
from math import ceil



class Organism(object):
	GLOBAL_PATHWAY_PATTERN = re.compile('01[12][0-9]{2}')
	"""
	Pattern defining a global/overview pathway.
	
	These pathways should contain nothing more and nothing less than what is included in all non-global pathways. At least concerning metabolic pathways.
	"""
	DIGITS_PATTERN = re.compile('\d+')
	
	def __init__(self, nameAbbreviation: 'eco', skipExistsCheck = False):
		"""
		An Organism as listed in KEGG, e.g. Escherichia coli K-12 MG1655 "eco".
		
		Checks whether the organism actually exists before creating the object.
		
		Parameters
		----------
		nameAbbreviation : str
			The abbreviation of an organism as used in KEGG.
		skipExistsCheck : bool
			If *True*, skips the check for existence of an organism identified by `nameAbbreviation`. Any subsequent method access may raise an error if the organism does not exist in KEGG!
			
		Raises
		------
		:class:`ValueError`
			If the organism does not exist at all in KEGG.
		IOError
			If the connection to the KEGG server fails and the requested organism has not already been cached.
		
		Note
		----
		All operations are cached via :class:`Database`. This includes any downloads and the calculations available directly via this class.
		"""
		self.nameAbbreviation = nameAbbreviation
		
		if skipExistsCheck is False and Database.doesOrganismExist(nameAbbreviation) is False:
			raise ValueError('Organism abbreviation does not exist: ' + nameAbbreviation)
	
	@classmethod
	def initBulk(cls, nameAbbreviations: List[str]) -> List['Organism']:
		"""
		Takes a list of organism abbreviations, checks if they exist, and returns a list of existing organism objects.
		If none of the organisms exist, returns None.
		"""
		existingOrganisms = Database.doesOrganismExistBulk(nameAbbreviations)
		if len(existingOrganisms) == 0:
			return None
		else:
			organisms = []
			
			# filter quirky organisms, without any pathway
			for nonExisting in quirks.NON_EXISTING_ORGANISMS:
				while True:
					try:
						existingOrganisms.remove(nonExisting)
					except ValueError:
						break
			
			for abbreviation in existingOrganisms:
				organism = cls(abbreviation, skipExistsCheck = True)
				organisms.append(organism)
			return organisms
	
	def __str__(self):
		return 'Organism(' + self.nameAbbreviation + ')'
	
	def __eq__(self, other):
		if isinstance(self, other.__class__):
			return self.nameAbbreviation == other.nameAbbreviation
		return False
	
	def __ne__(self, other):
		return not self == other
	
	def __hash__(self):
		return self.nameAbbreviation.__hash__()
	
	def __lt__(self, other):
		return self.nameAbbreviation.lower() < other.nameAbbreviation.lower()
	
	def __gt__(self, other):
		return self.nameAbbreviation.lower() > other.nameAbbreviation.lower()
	
	def __le__(self, other):
		return self.nameAbbreviation.lower() <= other.nameAbbreviation.lower()
	
	def __ge__(self, other):
		return self.nameAbbreviation.lower() >= other.nameAbbreviation.lower()
	
	def getPathway(self, pathwayName: '00260') -> KGML_pathway.Pathway:
		"""
		gets a certain pathway for this organism. If pathway does not exist, returns None.
		"""
		return Database.getPathway(self.nameAbbreviation, pathwayName)
	
	
	def getPathways(self, includeOverviewMaps = False) -> Set[KGML_pathway.Pathway]:
		"""
		gets a set of all pathway objects for this organism.
		"""
		return self.getPathwaysFromNames(self.getPathwayNames(self.getPathwayIDs(self.getPathwayDescriptions(includeOverviewMaps))))
	
	
	def getMetabolicPathways(self, includeOverviewMaps = False) -> Set[KGML_pathway.Pathway]:
		"""
		gets a set of all pathway objects for this organism.
		"""
		return self.getPathwaysFromNames(self.getPathwayNames(self.getPathwayIDs(self.getMetabolicPathwayDescriptions(includeOverviewMaps))))
	
	
	@property
	def metabolicPathways(self) -> Set[KGML_pathway.Pathway]:
		"""
		Pathways of metabolism, without overview or global maps.
		"""
		return self.getMetabolicPathways(includeOverviewMaps = False)
	
	
	def getPathwaysFromNames(self, pathwayNameSet: Set[str]) -> Set[KGML_pathway.Pathway]:
		"""
		gets a set of pathway objects for this organism, based on the list of pathway names, eg. ['00260', '01100'].
		"""
		return Database.getPathwayBulk(self.nameAbbreviation, pathwayNameSet).values()
	
	
	def getPathwayDescriptions(self, includeOverviewMaps = False) -> Set[str]:
		"""
		Get pathway description set for this organism.
		Does not include global and overview maps, unless includeOverviewMaps == True.
		"""
		descriptions = Database.getPathwayDescriptions(self.nameAbbreviation)
		if includeOverviewMaps == True:
			return descriptions
		else:
			return self.__class__._filterGlobalAndOverview(descriptions)
	
	
	@classmethod
	def _filterGlobalAndOverview(cls, pathwayDescriptions: Set[str]) -> Set[str]:
		"""
		Removes global and overview maps from the list of pathways.
		"""
		newSet = set()
		for pathwayString in pathwayDescriptions:
			if cls.GLOBAL_PATHWAY_PATTERN.search(pathwayString) is None: # not a global/overview map
				newSet.add(pathwayString)
		return newSet
	
	
	def getMetabolicPathwayDescriptions(self, includeOverviewMaps = False) -> Set[str]:
		"""
		Get descriptions of pathways that are part of metabolism.
		Does not include global and overview maps, unless includeOverviewMaps == True.
		"""
		descriptions = self.getPathwayDescriptions(includeOverviewMaps)
		return self._filterNonMetabolic(descriptions)
	
	
	def _filterNonMetabolic(self, pathwayDescriptions: Set[str]) -> Set[str]:
		"""
		Removes pathway descriptions not belonging to metabolism.
		"""
		newSet = set()
		for pathwayString in pathwayDescriptions:
			
			tempSet = set()
			tempSet.add(pathwayString)
			
			if self.getPathwayNames(self.getPathwayIDs(tempSet)).pop() in quirks.METABOLIC_PATHWAYS: # is a metabolism pathway
				newSet.add(pathwayString)
		
		return newSet
	
	
	def getPathwayIDs(self, pathwayDescriptions: Set[str]) -> Set[str]:
		"""
		get pathway set for this organism, keeping only the IDs (eg. 'eco00260'), no description.
		"""
		pathwayIDSet = set()
		for pathway in pathwayDescriptions:
			pathwayID = pathway.split('\t')[0].replace('path:','')
			pathwayIDSet.add(pathwayID)
		return pathwayIDSet
	
	
	def getPathwayNames(self, pathwayIDs: Set[str]) -> Set[str]:
		"""
		get pathway set for this organism, keeping only the Names (eg. '00260'), no description.
		"""
		pathwayNameSet = set()
		for pathwayID in pathwayIDs:
			pathwayNameSet.add(pathwayID.replace(self.nameAbbreviation, ''))
		return pathwayNameSet
	
	
	def printPathways(self):
		"""
		prints all pathways from pathway list of this organism. Does not include global or overview maps.
		"""
		pathwayList = self.getPathwayDescriptions()
		for pathway in pathwayList:
			print(pathway)
	
	
	def getGene(self, gene: 'eco:b0004 or b0004') -> Gene:
		"""
		get a certain gene object for this organism. Automatically recognises format.
		"""	
		if ':' in gene:
			return self.getGeneByID(gene)
		else:
			return self.getGeneByName(gene)
	
	
	def getGeneByName(self, geneName: 'b0004') -> Gene:
		"""
		get a certain gene object for this organism. Automatically prepends organism, eg. 'eco:'+geneName.
		"""
		gene = Database.getGene(self.nameAbbreviation + ':' + geneName)
		return gene
	
	
	def getGeneByID(self, geneID: 'eco:b0004') -> Gene:
		"""
		get a certain gene object for this organism. Does not check if the prefix matches this organism!
		"""
		gene = Database.getGene(geneID)
		return gene
	
	
	def getGeneIDs(self, pathway: 'KGML_pathway.Pathway or 00260') -> Set[str]:
		"""
		automatically chooses getGeneIDsByName() or getGeneIDsByPathway().
		get the list of all gene IDs of this organism for a pathway. ['eco:b0632', 'eco:b0839', 'eco:b2010']. Deduplicates original list.
		"""
		if pathway.__class__ == KGML_pathway.Pathway:
			return self.getGeneIDsByPathway(pathway)
		else:
			return self.getGeneIDsByName(pathway)
	
	
	def getGeneIDsByPathway(self, pathway: KGML_pathway.Pathway) -> Set[str]:
		"""
		get the set of all gene IDs of this organism for a pathway. ['eco:b0632', 'eco:b0839', 'eco:b2010']. Deduplicates original list.
		"""
		pathwayNumber = self.__class__.DIGITS_PATTERN.findall(pathway.name)[0]
		geneNameList = Database.getPathwayGeneIDs(self.nameAbbreviation, pathwayNumber) # try to get list from disk
		
		# if not on disk, calculate the list
		if geneNameList == None:
			geneNameList = self._calculateGeneIDs(pathway, pathwayNumber)
			
		return geneNameList
		
	
	def getGeneIDsByName(self, pathwayName: '00260') -> Set[str]:
		"""
		get the set of all gene IDs of this organism for a pathway. ['eco:b0632', 'eco:b0839', 'eco:b2010']. Deduplicates original list.
		"""
		geneNameList = Database.getPathwayGeneIDs(self.nameAbbreviation, pathwayName) # try to get list from disk
		
		# if not on disk, calculate the list
		if geneNameList == None:
			geneNameList = self._calculateGeneIDs(self.getPathway(pathwayName), pathwayName)
			
		return geneNameList
	
	
	def _calculateGeneIDs(self, pathway: KGML_pathway.Pathway, pathwayName: '00260') -> Set[str]:
		geneNameSet = set()
		geneDescriptionList = pathway.genes
		for geneDescription in geneDescriptionList:
			namePossiblyList = geneDescription.name
			
			nameList = namePossiblyList.split(' ')
			
			for name in nameList:
				geneNameSet.add(name)
		
		Database.setPathwayGeneIDs(self.nameAbbreviation, pathwayName, geneNameSet) # cache the deduplicated list to disk
		
		return geneNameSet
			
	
	def getGenes(self, pathway: 'KGML_pathway.Pathway or 00260') -> Set[Gene]:
		"""
		automatically chooses getGenesByName() or getGenesByPathway()
		"""
		if pathway.__class__ == KGML_pathway.Pathway:
			return self.getGenesByPathway(pathway)
		else:
			return self.getGenesByName(pathway)
	
	
	def getGenesByName(self, pathwayName: '00260') -> Set[Gene]:
		"""
		get the set of all gene objects of this organism's pathway. Deduplicates original list.
		"""
		geneList = set()
		
		geneIDList = self.getGeneIDsByName(pathwayName)
		
		for geneID in geneIDList:
			geneList.add(self.getGeneByID(geneID))
			
		return geneList
	
	
	def getGenesByPathway(self, pathway: KGML_pathway.Pathway) -> Set[Gene]:
		"""
		get the set of all gene objects of this organism's pathway. Deduplicates original list.
		"""
		geneList = set()
		
		geneIDList = self.getGeneIDsByPathway(pathway)
		
		for geneID in geneIDList:
			geneList.add(self.getGeneByID(geneID))
			
		return geneList
	
	
	def substrateEcGraph(self, noMultifunctional = False, returnCacheEntry = False) -> SubstrateEcGraph:
		"""
		substrate-EC graph
		"""
		file_name = 'SubstrateEcGraph'
		if noMultifunctional is True:
			file_name += '_noMultifunctional'
		
		folder_path = 'organism/' + self.nameAbbreviation + '/graph'
		
		if returnCacheEntry is False: # shall return result
			decorator = cache(folder_path = folder_path, file_name = file_name)
		else: # shall return CacheEntry object
			decorator = cacheEntry(folder_path = folder_path, file_name = file_name)
			
		function = lambda: Conversion.SubstrateEnzymeGraph2SubstrateEcGraph(self.substrateEnzymeGraph(noMultifunctional))
		return decorator(function)()
	
	def substrateEnzymeGraph(self, noMultifunctional = False, returnCacheEntry = False) -> SubstrateEnzymeGraph:
		"""
		substrate-enzyme graph
		"""
		file_name = 'SubstrateEnzymeGraph'
		if noMultifunctional is True:
			file_name += '_noMultifunctional'
		
		folder_path = 'organism/' + self.nameAbbreviation + '/graph'
		
		if returnCacheEntry is False: # shall return result
			decorator = cache(folder_path = folder_path, file_name = file_name)
		else: # shall return CacheEntry object
			decorator = cacheEntry(folder_path = folder_path, file_name = file_name)
		
		function = lambda: Conversion.SubstrateGeneGraph2SubstrateEnzymeGraph(self.substrateGeneGraph(), noMultifunctional)
		return decorator(function)()
	
	def substrateGeneGraph(self, returnCacheEntry = False) -> SubstrateGeneGraph:
		"""
		substrate-gene graph
		"""
		file_name = 'SubstrateGeneGraph'
		folder_path = 'organism/' + self.nameAbbreviation + '/graph'
		
		if returnCacheEntry is False: # shall return result
			decorator = cache(folder_path = folder_path, file_name = file_name)
		else: # shall return CacheEntry object
			decorator = cacheEntry(folder_path = folder_path, file_name = file_name)
		
		function = lambda: Conversion.SubstrateReactionGraph2SubstrateGeneGraph(self.substrateReactionGraph())
		return decorator(function)()
	
	def substrateReactionGraph(self, returnCacheEntry = False) -> SubstrateReactionGraph:
		"""
		substrate-reaction graph
		"""
		file_name = 'SubstrateReactionGraph'
		folder_path = 'organism/' + self.nameAbbreviation + '/graph'
		
		if returnCacheEntry is False: # shall return result
			decorator = cache(folder_path = folder_path, file_name = file_name)
		else: # shall return CacheEntry object
			decorator = cacheEntry(folder_path = folder_path, file_name = file_name)
		
		function = lambda: Conversion.KeggPathwaySet2SubstrateReactionGraph(self.getMetabolicPathways(), name = self.nameAbbreviation)
		return decorator(function)()
	






	
	
class Group(object):
	
	def __init__(self, organismAbbreviations: Iterable[str] = None, searchString: 'any part of organism description' = None, name = None):
		"""
		Creates a Group of Organisms.
		
		If searchString != None:
		Searches the list of all organisms known to KEGG for the passed string. An entry of the KEGG list of organisms looks as follows:
		T00338	eci	Escherichia coli O18:K1:H7 UTI89 (UPEC)	Prokaryotes;Bacteria;Gammaproteobacteria - Enterobacteria;Escherichia
		Any list entry matching the search string creates an Organism object
		
		If organismAbbreviations != None:
		Tries to find an Organism object for each abbreviation in the list.
		
		If both parameters are specified:
		Both lists will be appended, forming this object's list of Organisms.
		
		If none of the parameters is specified:
		This Group has an empty organism list.
		"""
		self._collectiveEcGraph = None
		self._collectiveEcGraph_noMultifunctional = None
		
		self.searchString = searchString
		self.__organisms = set()
		
		if searchString is not None:
			organismList = Database.getOrganismList()
			
			matchList = []
			
			for entry in organismList:
				if searchString in entry:
					entrySplit = entry.split('\t')
					matchList.append(entrySplit[1])
			
			organisms = Organism.initBulk(matchList)
			self.__organisms.update(organisms)
		
		if organismAbbreviations is not None:
			listObject = []
			listObject.extend(organismAbbreviations)
			organisms = Organism.initBulk(listObject)
			self.__organisms.update(organisms)
		
		self.name = name
	
	def __str__(self):
		return 'Group(' + self.organisms + ')'

	def __eq__(self, other):
		if isinstance(self, other.__class__):
			return self.organisms == other.organisms
		return False

	def __ne__(self, other):
		return not self == other

	def __hash__(self):
		return self.organisms.__hash__()
	
	def freeHeap(self):
		"""
		Removes objects kept on heap, i.e. which have a pointer kept in this object, because some function was called with 'keepOnHeap'==True
		Also calls garbage collector to break reference cycles in previously uncollected objects (generation 0).
		"""
		self._collectiveEcGraph = None
		self._collectiveEcGraph_noMultifunctional = None
		gc.collect(0)
	
	
	@property
	def organisms(self) -> Set[Organism]:
		"""
		Returns the set of organisms which are part of this group.
		"""
		return self.__organisms
	
	@property
	def organismsCount(self) -> int:
		"""
		Returns the number of organisms in the set of organisms of this group.
		"""
		return len( self.__organisms )
	
	
	
	
	def enzymeGraphs(self, noMultifunctional = False) -> List[SubstrateEnzymeGraph]:
		"""
		Returns SubstrateEnzymeGraphs of all organisms in this group. Order is arbitrary.
		"""
		return self._getGraphsParallelly(self._enzymeGraphsWorker, self.organisms, noMultifunctional, 'enzyme graphs')
	
	def _enzymeGraphsWorker(self, organism: Organism, noMultifunctional, returnCacheEntry) -> SubstrateEnzymeGraph:
		return organism.substrateEnzymeGraph(noMultifunctional, returnCacheEntry)
	
	def ecGraphs(self, noMultifunctional = False) -> List[SubstrateEcGraph]:
		"""
		Returns SubstrateEcGraphs of all organisms in this group. Order is arbitrary.
		"""
		return self._getGraphsParallelly(self._ecGraphsWorker, self.organisms, noMultifunctional, 'EC graphs')
	
	def _ecGraphsWorker(self, organism: Organism, noMultifunctional, returnCacheEntry) -> SubstrateEcGraph:
		return organism.substrateEcGraph(noMultifunctional, returnCacheEntry)
	
	def _getGraphsParallelly(self, worker, organisms, noMultifunctional, debugText):
		
		threadPool = concurrent.futures.ThreadPoolExecutor(Parallelism.getNumberOfThreadsFile())
		futures = []
		futuresIO = []
		futuresGenerator = None
		resultFutures = None
		
		try:
			
			# submit work to process pool
			for organism in organisms:
				if Parallelism.processPool is None:
					raise TypeError("Process pool does not exist. Did you forget to FEV_KEGG.startProcessPool()?")
				futures.append( Parallelism.processPool.submit( worker, organism, noMultifunctional, True ) )
				
			futuresGenerator = concurrent.futures.as_completed( futures )
			
			# add progress bar
			if settings.verbosity >= 1:
				if settings.verbosity >= 2:
					print( 'Fetching ' + debugText + ' from ' + str(len(organisms)) + ' organisms...' )
				futuresGenerator = tqdm.tqdm(futuresGenerator, total = len(organisms), unit = ' organisms', position = 0)
			
			# when any work item in process pool finishes
			for future in futuresGenerator: # TODO: add infinite wait detection
				
				try:
					cacheEntry = future.result()
				except KeyboardInterrupt:
					raise
				except concurrent.futures.CancelledError:
					Parallelism.printBelowProgress( "Future cancelled. Continuing anyway..." )
					continue
				except concurrent.futures.TimeoutError:
					Parallelism.printBelowProgress( "Future timed out. Continuing anyway..." )
					continue
				except NoKnownPathwaysError as e: # organism has no known pathways, ignore it
					Parallelism.printBelowProgress( "Future raised error: " + str(e) + " Ignoring this organism." )
					continue
				except Exception: # any non-exiting error
					Parallelism.printBelowProgress( "Future raised error, see stack trace above. Halting by KeyboardInterrupt..." )
					raise KeyboardInterrupt()
				
				futuresIO.append( threadPool.submit(cacheEntry.getResult) )
			
			resultFutures = concurrent.futures.as_completed( futuresIO )
			
			if settings.verbosity >= 2:
				if settings.verbosity >= 2:
					print( 'Doing I/O for ' + str(len(organisms)) + ' organisms...' )
				resultFutures = tqdm.tqdm(resultFutures, total = len(organisms), unit = ' organism I/Os', position = 0)
			
			graphs = []
			for future in resultFutures:
				graphs.append( future.result() )
			
			return graphs
		
		except KeyboardInterrupt: # only raised in main thread (once in each process!)
			
			Parallelism.keyboardInterruptHandler(processPoolFutures=futures, threadPool=threadPool, threadPoolFutures=futuresIO, terminateProcess=True)
			raise

		except BaseException:
			
			if Parallelism.isMainThread():
				Parallelism.keyboardInterruptHandler(processPoolFutures=futures, threadPool=threadPool, threadPoolFutures=futuresIO, silent=True)
			raise
		
		finally:
			
			if threadPool is not None: threadPool.shutdown(wait = False)			
			if futuresGenerator is not None: futuresGenerator.close()
			if resultFutures is not None: resultFutures.close()
			
			Parallelism.printBelowProgress(None)

	
	
	
	def collectiveEcGraph(self, noMultifunctional = False, addCount = False, keepOnHeap = True) -> SubstrateEcGraph:
		"""
		Returns a collective of all SubstrateEcGraphs, by union operation, from all organisms in this group.
		Nodes of the same Substrate are merged, all edges of differing ECs with a unique pair of nodes survive.
		
		If 'addCount' == True, the returned graph contains extra dicts:
		- graph.substrateCounts[Substrate] = number of organisms which contained this Substrate
		- graph.edgeCounts[(Substrate, Product, EcNumber)] = number of organisms which contained this edge, i.e. the tuple of Substrates and the EcNumber 
		- graph.ecCounts[EcNumber] = number of organisms which contained this EcNumber

		Attention! These counter dictionaries are NOT updated if your add or remove a node/edge/element!

		If 'keepOnHeap' == True, keeps a pointer to the collective SubstrateEcGraph in this Group object.
		This can take up a lot of memory! Once this object is garbage collected, the collective SubstrateEcGraph will be, too.
		"""
		if keepOnHeap is True: # shall keep the result on heap
			# check first if it already is on heap
			if noMultifunctional is True:
				collectiveEcGraph = self._collectiveEcGraph_noMultifunctional
			else:
				collectiveEcGraph = self._collectiveEcGraph
			
			if collectiveEcGraph is not None:
				return collectiveEcGraph
			
			
		allSubstrateEcGraphs = self.ecGraphs(noMultifunctional)
		if isinstance(allSubstrateEcGraphs, Generator):
			lastGraph = allSubstrateEcGraphs.next()
		else:
			lastGraph = allSubstrateEcGraphs.pop()
		collectiveGraph = lastGraph.union(allSubstrateEcGraphs, addCount = addCount)
		if self.name is None:
			collectiveGraph.name = 'Collective EC graph'
		else:
			collectiveGraph.name = 'Collective EC graph ' + self.name
		
		if keepOnHeap is True: # shall keep the result on heap
			# save the calculated result on heap
			if noMultifunctional is True:
				self._collectiveEcGraph_noMultifunctional = collectiveGraph
			else:
				self._collectiveEcGraph = collectiveGraph
		
		return collectiveGraph
			
		
	
	def consensusEcGraph(self, noMultifunctional = False, keepOnHeap = True) -> SubstrateEcGraph:
		"""
		Returns a consensus of all SubstrateEcGraphs, by intersection operation, from all organisms in this group.
		Afterwards, removes isolated nodes.
		
		If 'keepOnHeap' == True, keeps a pointer to the collective SubstrateEcGraph in this Group object.
		This can take up a lot of memory! Once the Group is garbage collected, the collective SubstrateEcGraph will be, too.
		"""
		if settings.verbosity >= 1:
			print('calculating consensus EC graph...')
		
		if keepOnHeap is True:
			
			originalCollectiveEcGraph = self.collectiveEcGraph(noMultifunctional, addCount = True, keepOnHeap = True) 
			collectiveEcGraph = originalCollectiveEcGraph.copy()
			edgeCounts = originalCollectiveEcGraph.edgeCounts
			
			edgesToBeRemoved = []
			for edge, count in edgeCounts.items():
				if count < self.organismsCount: # has not occured in enough organisms
					edgesToBeRemoved.append(edge)
			
			collectiveEcGraph.removeEcEdges(edgesToBeRemoved)
			collectiveEcGraph.removeIsolatedNodes()
			
			if self.name is None:
				collectiveEcGraph.name = 'Consensus EC graph'
			else:
				collectiveEcGraph.name = 'Consensus EC graph ' + self.name
			
			return collectiveEcGraph
			
		else:
			
			allSubstrateEcGraphs = self.ecGraphs(noMultifunctional)
			if isinstance(allSubstrateEcGraphs, Generator):
				lastGraph = allSubstrateEcGraphs.next()
			else:
				lastGraph = allSubstrateEcGraphs.pop()
			consensusGraph = lastGraph.intersection(allSubstrateEcGraphs)
			consensusGraph.removeIsolatedNodes()
			
			if self.name is None:
				consensusGraph.name = 'Consensus EC graph'
			else:
				consensusGraph.name = 'Consensus EC graph ' + self.name
			
			return consensusGraph
		
	def majorityEcGraph(self, majorityPercentage = 90, majorityTotal = None, noMultifunctional = False, keepOnHeap = True) -> SubstrateEcGraph:
		"""
		Returns a majority-consensus of all SubstrateEcGraphs, by majority-intersection operation, from all organisms in this group.
		If the majority of organisms contains an edge, it is added to the majority-consensus.
		The majority percentage means 'at least x%' and is rounded up. For example 90% of 11 organisms would be ceiling(9,9) = 10 organisms.
		If 'majorityTotal' is given (not None), majorityPercentage is ignored and the percentage of organisms for a majority is calculated from majorityTotal.
		Afterwards, removes isolated nodes.
		
        If 'keepOnHeap' == True, keeps a pointer to the collective SubstrateEcGraph in this Group object.
        This can take up a lot of memory! Once the Group is garbage collected, the collective SubstrateEcGraph will be, too.
		"""
		if settings.verbosity >= 1:
			print('calculating majority EC graph...')
		
		if majorityTotal is not None:
			percentage = majorityTotal / self.organismsCount * 100
		else:
			percentage = majorityPercentage
			
		if keepOnHeap is True:
			
			# check if majorityPercentage is sane
			if majorityPercentage <= 0 or majorityPercentage > 100:
				raise ValueError('Majority percentage is not a sane value (0 < percentage <= 100): ' + str(majorityPercentage))
			majorityTotal = ceil((majorityPercentage/100) * self.organismsCount)
			
			originalCollectiveEcGraph = self.collectiveEcGraph(noMultifunctional, addCount = True, keepOnHeap = True)
			collectiveEcGraph = originalCollectiveEcGraph.copy()
			edgeCounts = originalCollectiveEcGraph.edgeCounts
			
			edgesToBeRemoved = []
			for edge, count in edgeCounts.items():
				if count < majorityTotal: # has not occured in enough organisms
					edgesToBeRemoved.append(edge)
			
			collectiveEcGraph.removeEcEdges(edgesToBeRemoved)
			collectiveEcGraph.removeIsolatedNodes()
			
			if self.name is None:
				collectiveEcGraph.name = 'Majority EC graph'
			else:
				collectiveEcGraph.name = 'Majority EC graph ' + self.name
			
			return collectiveEcGraph
		
		else:
			
			allSubstrateEcGraphs = self.ecGraphs(noMultifunctional)
			if isinstance(allSubstrateEcGraphs, Generator):
				lastGraph = allSubstrateEcGraphs.next()
			else:
				lastGraph = allSubstrateEcGraphs.pop()
			majorityGraph = lastGraph.majorityIntersection(allSubstrateEcGraphs, percentage)
			majorityGraph.removeIsolatedNodes()
			
			if self.name is None:
				majorityGraph.name = 'Majority EC graph'
			else:
				majorityGraph.name = 'Majority EC graph ' + self.name
			
			return majorityGraph
	
	
	
	
	
	def collectiveEnzymeGraph(self, noMultifunctional = False) -> SubstrateEnzymeGraph:
		"""
		Returns a collective of all SubstrateEnzymeGraphs, by union operation, from all organisms in this group.
		Nodes of the same Substrate are merged, all edges of differing Enzymes with a unique pair of nodes survive. Enzymes are compared by their GeneID and should, thus, all be different!
		"""
		if settings.verbosity >= 1:
			print('calculating collective enzyme graph...')
		
		allSubstrateEnzymeGraphs = self.enzymeGraphs(noMultifunctional)
		if isinstance(allSubstrateEnzymeGraphs, Generator):
			lastGraph = allSubstrateEnzymeGraphs.next()
		else:
			lastGraph = allSubstrateEnzymeGraphs.pop()
		collectiveGraph = lastGraph.union(allSubstrateEnzymeGraphs)
		
		if self.name is None:
			collectiveGraph.name = 'Collective Enzyme graph'
		else:
			collectiveGraph.name = 'Collective Enzyme graph ' + self.name
		
		return collectiveGraph
	

	def collectiveEnzymeGraphByEcConsensus(self, noMultifunctional = False) -> SubstrateEnzymeGraph:
		"""
		Returns a collective SubstrateEnzymGraph from all organisms in this group, but containing only Enzymes whose EC numbers occur in the consensus of all SubstrateEcGraphs.
		"""
		return self.collectiveEnzymeGraphByEcMajority(majorityPercentage = 100, majorityTotal = None, noMultifunctional = noMultifunctional)
		
	
	def collectiveEnzymeGraphByEcMajority(self, majorityPercentage = 90, majorityTotal = None, noMultifunctional = False) -> SubstrateEnzymeGraph:
		"""
		Returns a collective SubstrateEnzymGraph from all organisms in this group, but containing only Enzymes whose EC numbers occur in the majority of all SubstrateEcGraphs.
		"""
		if majorityPercentage >= 100:
			ecNumbers = self.consensusEcGraph(noMultifunctional).getECs()
			
		else:
			ecNumbers = self.majorityEcGraph(majorityPercentage, majorityTotal, noMultifunctional).getECs()
		
		collectiveEnzymeGraph = self.collectiveEnzymeGraph(noMultifunctional)
		
		collectiveEnzymeGraph.removeEnzymesByEC(ecNumbers, keepInstead = True)
		
		collectiveEnzymeGraph.name += ' by EC majority'
		
		return collectiveEnzymeGraph
		
	