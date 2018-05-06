import math

from typing import Set, Dict

from FEV_KEGG.Graph.Elements import Enzyme, EcNumber
from FEV_KEGG.Graph.SubstrateGraphs import SubstrateEnzymeGraph, SubstrateEcGraph
from FEV_KEGG.KEGG import Database
from builtins import set
from FEV_KEGG.KEGG.Organism import Group
from _collections_abc import Iterable

defaultEValue = 1e-15

class GeneFunctionConservation(object):
    """
    The conditions for a gene function conservation are:
        - The EC number has been conserved, along the way from an older group of organisms to a newer one.
    """
    @staticmethod
    def getConservedECs(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> Set[EcNumber]:
        """
        Returns a Set of EC numbers which occur in the ancestor's EC graph and in the decendants's, ie. EC numbers which are conserved in the descendant.
        """
        conservedECs = ancestorEcGraph.getECs()
        conservedECs.intersection_update(descendantEcGraph.getECs())
        return conservedECs
    
    @staticmethod
    def getConservedGraph(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> SubstrateEcGraph:
        """
        Returns the SubstrateEcGraph of EC numbers which occur in the ancestor's EC graph, but not in the decendants's, ie. EC numbers which are conserved in the descendant.
        """
        conservedGraph = ancestorEcGraph.intersection(descendantEcGraph, addCount=False)
        conservedGraph.removeIsolatedNodes()
        return conservedGraph
    
    
class GeneFunctionAddition(object):
    """
    The conditions for a gene function addition are:
        - The EC number has been added, from an unknown origin, along the way from an older group of organisms to a newer one.
    """
    @staticmethod
    def getAddedECs(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> Set[EcNumber]:
        """
        Returns a Set of EC numbers which occur in the descendant's EC graph, but not in the ancestor's, ie. EC numbers which are new to the descendant.
        """
        addedECs = descendantEcGraph.getECs()
        addedECs.difference_update(ancestorEcGraph.getECs())
        return addedECs
    
    @staticmethod
    def getAddedGraph(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> SubstrateEcGraph:
        """
        Returns the SubstrateEcGraph of EC numbers which occur in the descendant's EC graph, but not in the ancestor's, ie. EC numbers which are new to the descendant.
        """
        addedGraph = descendantEcGraph.difference(ancestorEcGraph, subtractNodes=False)
        addedGraph.removeIsolatedNodes()
        return addedGraph


class GeneFunctionLoss(object):
    """
    The conditions for a gene function loss are:
        - The EC number has been lost, along the way from an older group of organisms to a newer one.
    """
    @staticmethod
    def getLostECs(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> Set[EcNumber]:
        """
        Returns a Set of EC numbers which occur in the ancestor's EC graph, but not in the decendants's, ie. EC numbers which are lost in the descendant.
        """
        lostECs = ancestorEcGraph.getECs()
        lostECs.difference_update(descendantEcGraph.getECs())
        return lostECs
    
    @staticmethod
    def getLostGraph(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> SubstrateEcGraph:
        """
        Returns the SubstrateEcGraph of EC numbers which occur in the ancestor's EC graph, but not in the decendants's, ie. EC numbers which are lost in the descendant.
        """
        lostGraph = ancestorEcGraph.difference(descendantEcGraph, subtractNodes=False)
        lostGraph.removeIsolatedNodes()
        return lostGraph


class GeneFunctionDivergence(object):
    """
    The conditions for a gene function divergence are:
        - The EC number exists in an older group of organisms, but not in a newer one, or the other way around.
    """
    @staticmethod
    def getDivergedECs(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> Set[EcNumber]:
        """
        Returns a Set of EC numbers which occur in the ancestor's EC graph, but not in the decendants's and vice versa, ie. EC numbers which only exist in either one of the organism groups.
        Obviously, 'ancestorEcGraph' and 'descendantEcGraph' can be swapped here without changing the result.
        """
        divergedECs = ancestorEcGraph.getECs()
        divergedECs.symmetric_difference(descendantEcGraph.getECs())
        return divergedECs
    
    @staticmethod
    def getDivergedGraph(ancestorEcGraph: SubstrateEcGraph, descendantEcGraph: SubstrateEcGraph) -> SubstrateEcGraph:
        """
        Returns the SubstrateEcGraph of EC numbers which occur in the ancestor's EC graph, but not in the decendants's and vice versa, ie. EC numbers which only exist in either one of the organism groups.
        """
        addedGraph = GeneFunctionAddition.getAddedGraph(ancestorEcGraph, descendantEcGraph)
        lostGraph = GeneFunctionLoss.getLostGraph(ancestorEcGraph, descendantEcGraph)
        divergedGraph = addedGraph.union(lostGraph, addCount=False)
        return divergedGraph






class GeneDuplication(object): 
    """
    Abstract class for any type of gene duplication
    """

class SimpleGeneDuplication(GeneDuplication):
    """
    The conditions for a 'simple' gene duplication are:
        - The gene has at least one paralog.
    """    
    @staticmethod
    def getEnzymesFromSet(enzymes: Set[Enzyme], eValue = defaultEValue) -> Set[Enzyme]:
        """
        Returns a Set of all Enzymes in 'enzymes' which fulfil the conditions of this gene duplication definition.
        """
        possibleGeneDuplicates = set()
        
        geneIDs = [enzyme.geneID for enzyme in enzymes]
        
        matchingsDict = Database.getParalogsBulk(geneIDs, eValue)
        
        for enzyme in enzymes:
            matching = matchingsDict[enzyme.geneID]
            paralogs = matching.matches
            if len(paralogs) > 0:
                possibleGeneDuplicates.add(enzyme)
        
        return possibleGeneDuplicates
    
    @classmethod
    def getEnzymesFromGraph(cls, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> Set[Enzyme]:
        """
        Returns a Set of all Enzymes in 'substrateEnzymeGraph' which fulfil the conditions of this gene duplication definition.
        """
        return cls.getEnzymesFromSet(substrateEnzymeGraph.getEnzymes(), eValue)
    
    @classmethod
    def filterEnzymes(cls, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Returns a copy of the SubstrateEnzymeGraph containing only Enzymes which fulfil the conditions of this gene duplication definition.
        """
        graph = substrateEnzymeGraph.copy()
        possibleGeneDuplicates = cls.getEnzymesFromGraph(substrateEnzymeGraph, eValue)
        graph.removeAllEnzymesExcept( possibleGeneDuplicates )
        return graph
        
    

class ChevronGeneDuplication(GeneDuplication):
    """
    The conditions for a 'chevron' gene duplication are:
        - The gene has at least one paralog.
        - The gene has at least one ortholog in a pre-defined set of organisms.
    """
    def __init__(self, possiblyOrthologousOrganisms: 'Iterable[Organism] or KEGG.Organism.Group'):
        """
        Chevron gene duplication, extends simple gene duplication by restricting the possibly duplicated genes via a set of possibly orthologous organisms.
        'possiblyOrthologousOrganisms' is a set of organisms which will be searched for the occurence of orthologs, also accepts a Group object.
        """
        if isinstance(possiblyOrthologousOrganisms, Group):
            self.possiblyOrthologousOrganisms = possiblyOrthologousOrganisms.organisms
        elif isinstance(possiblyOrthologousOrganisms, Iterable):
            self.possiblyOrthologousOrganisms = possiblyOrthologousOrganisms
        else:
            raise ValueError("'possiblyOrthologusOrganisms' must be of type Iterable or KEGG.Organism.Group")
    
    def getAllOrthologsForEnzymesFromSet(self, enzymes: Set[Enzyme], eValue = defaultEValue) -> Dict[Enzyme, Set[Enzyme]]:
        """
        Returns a Dict of all Enzymes in 'enzymes' which fulfil the conditions of this gene duplication definition, each pointing to a set of ALL their possible orthologs.
        WARNING! This is a very slow operation, because all orthologs in all `self.possiblyOrthologousOrganisms` for all Enzymes are retrieved.
        """
        possibleGeneDuplicates = SimpleGeneDuplication.getEnzymesFromSet(enzymes, eValue)
        
        orthologsDict = dict()
        
        if len( possibleGeneDuplicates ) == 0:
            return orthologsDict
        
        geneIDs = [enzyme.geneID for enzyme in possibleGeneDuplicates]
        
        # reagarding each possibly orthologous organism
        for comparisonOrganism in self.possiblyOrthologousOrganisms: #TODO: parallelise with process pool
            # get orthologs
            matchingsDict = Database.getOrthologsBulk(geneIDs, comparisonOrganism, eValue)
            
            # regarding each paralogous enzyme
            for enzyme in possibleGeneDuplicates:
                # save orthologous GeneIDs for future conversion into Enzymes
                matching = matchingsDict[enzyme.geneID]
                orthologsMatches = matching.matches
                if len(orthologsMatches) > 0:
                    orthologsGeneIDs = set([match.foundGeneID for match in orthologsMatches])
                    
                    currentEntry = orthologsDict.get(enzyme, None)
                    if currentEntry is None:
                        orthologsDict[enzyme] = orthologsGeneIDs
                    else:
                        orthologsDict[enzyme] = currentEntry.update( orthologsGeneIDs )
        
        # regarding each paralogous enzyme
        for enzyme in possibleGeneDuplicates:
            # convert GeneIDs into Enzymes
            currentEntry = orthologsDict.get(enzyme, None)
            if currentEntry is not None:
                orthologsDict[enzyme] = set( [Enzyme.fromGene(gene) for gene in Database.getGeneBulk(currentEntry).values() ] )

        else:
            return orthologsDict
    
    def getEnzymesFromSet(self, enzymes: Set[Enzyme], eValue = defaultEValue) -> Set[Enzyme]:
        """
        Returns a Set of all Enzymes in 'enzymes' which fulfil the conditions of this gene duplication definition.
        """
        possibleGeneDuplicates = SimpleGeneDuplication.getEnzymesFromSet(enzymes, eValue)
        
        if len( possibleGeneDuplicates ) == 0:
            return possibleGeneDuplicates
        
        soughtEnzymes = possibleGeneDuplicates
        
        # ensure deterministic behaviour. Otherwise, this would null the use of the cache.
        sortedOrganisms = []
        sortedOrganisms.extend( self.possiblyOrthologousOrganisms )
        sortedOrganisms.sort()
        
        duplicatedEnzymes = set()
        
        # reagarding each possibly orthologous organism
        for comparisonOrganism in sortedOrganisms: #TODO: parallelise with process pool
            
            # break if nothing left to search for
            if len(soughtEnzymes) == 0:
                break
            
            # get orthologs
            geneIDs = [enzyme.geneID for enzyme in soughtEnzymes]
            matchingsDict = Database.getOrthologsBulk(geneIDs, comparisonOrganism, eValue)
            
            enzymesToRemove = set()
            
            # regarding each paralogous enzyme still sought
            for enzyme in soughtEnzymes:
                # count orthologous GeneIDs
                matching = matchingsDict[enzyme.geneID]
                orthologsMatches = matching.matches
                if len(orthologsMatches) > 0:
                    duplicatedEnzymes.add(enzyme)
                    enzymesToRemove.add(enzyme)
                    
            # remove found Enzyme from list of sought after Enzymes
            soughtEnzymes.difference_update(enzymesToRemove)
        
        return duplicatedEnzymes
        
    
    def getOrthologsForEnzymesFromGraph(self, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> Dict[Enzyme, Set[Enzyme]]:
        """
        Returns a Dict of all Enzymes in 'substrateEnzymeGraph' which fulfil the conditions of this gene duplication definition, each pointing to a set of ALL their possible orthologs.
        WARNING! This is a very slow operation, because all orthologs in all `self.possiblyOrthologousOrganisms` for all Enzymes are retrieved.
        """
        return self.getAllOrthologsForEnzymesFromSet(substrateEnzymeGraph.getEnzymes(), eValue)
    
    def getEnzymesFromGraph(self, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> Set[Enzyme]:
        """
        Returns a Set of all Enzymes in 'substrateEnzymeGraph' which fulfil the conditions of this gene duplication definition.
        """
        return self.getEnzymesFromSet(substrateEnzymeGraph.getEnzymes(), eValue)
    
    def filterEnzymes(self, substrateEnzymeGraph: SubstrateEnzymeGraph, eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Returns a copy of the SubstrateEnzymeGraph containing only Enzymes which fulfil the conditions of this gene duplication definition.
        """
        graph = substrateEnzymeGraph.copy()
        possibleGeneDuplicates = self.getEnzymesFromGraph(substrateEnzymeGraph, eValue)
        graph.removeAllEnzymesExcept( possibleGeneDuplicates )
        return graph





class Neofunctionalisation(object):
    """
    The conditions for a neofunctionalisation are:
        - The gene has been duplicated, along the way from an older group of organisms to a newer one, according to a certain class of GeneDuplication.
        - The duplicated gene is associated with an EC number which does not occur in the older group of organisms.
    """
    getNewECs = GeneFunctionAddition.getAddedECs
    


class AnyNeofunctionalisation(Neofunctionalisation):
    """
    Regarding groups of organisms, the conditions of this neofunctionalisation extend with:
        - At least one organism of the descendant group has to contain a gene duplicated enzyme for it (the enzyme or its EC number) to be reported.
    """
    @staticmethod
    def getEnzymesForEC(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                        newECs: Set[EcNumber], eValue = defaultEValue) -> Dict[EcNumber, Set[Enzyme]]:
        """
        Returns a Dict of Sets of Enzymes which fulfil the conditions of neofunctionalisation, keyed by the new EC numbers.
        """
        result = dict()
        
        # for each new EC number, get enzymes in descendant
        for ecNumber in newECs:
            enzymes = descendantEnzymeGraph.getEnzymesForEcNumber(ecNumber)
            
            # which of these enzymes have been subject to gene duplication? Report them.
            if isinstance(geneDuplicationModel, SimpleGeneDuplication) or geneDuplicationModel == SimpleGeneDuplication:
                duplicatedEnzymes = geneDuplicationModel.getEnzymesFromSet(enzymes, eValue)
            
            elif geneDuplicationModel == ChevronGeneDuplication:
                raise ValueError("Chevron gene duplication model requires you to instantiate an object, parametrised with the set of possibly orthologous organisms.")
                
            elif isinstance(geneDuplicationModel, ChevronGeneDuplication):
                duplicatedEnzymes = geneDuplicationModel.getEnzymesFromSet(enzymes, eValue)
                
            else:
                raise NotImplementedError('gene duplication model not yet known: ' + str(geneDuplicationModel))
            
            if len(duplicatedEnzymes) != 0:
                result[ecNumber] = duplicatedEnzymes 
        
        return result
    
    @staticmethod
    def getEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                   newECs: Set[EcNumber], eValue = defaultEValue) -> Set[Enzyme]:
        """
        Returns a Set of Enzymes which fulfil the conditions of neofunctionalisation.
        """
        resultDict = AnyNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue)
        resultSets = resultDict.values()
        result = set()
        for resultSet in resultSets:
            result.update( resultSet )
        return result
    
    @staticmethod
    def filterEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                      newECs: Set[EcNumber], eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Returns a copy of the descendant's SubstrateEnzymeGraph containing only Enzymes which fulfil the conditions of this neofunctionalisation.
        """
        graph = descendantEnzymeGraph.copy()
        possibleNeofunctionalisations = AnyNeofunctionalisation.getEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue)
        graph.removeAllEnzymesExcept( possibleNeofunctionalisations )
        return graph
    
    @staticmethod
    def getECs(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
               newECs: Set[EcNumber], eValue = defaultEValue) -> Set[EcNumber]:
        """
        Returns a Set of EC numbers which fulfil the conditions of neofunctionalisation.
        """
        return set( AnyNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue).keys() )
    
    @staticmethod
    def filterECs(descendantEcGraph: SubstrateEcGraph,
                  descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                  newECs: Set[EcNumber], eValue = defaultEValue) -> SubstrateEcGraph:
        """
        Returns a copy of the descendant's SubstrateEcGraph containing only EC numbers which fulfil the condition of this neofunctionalisation.
        """
        graph = descendantEcGraph.copy()
        possibleNeofunctionalisations = AnyNeofunctionalisation.getECs(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue)
        graph.removeAllECsExcept( possibleNeofunctionalisations )
        return graph
    
        

class MajorityNeofunctionalisation(Neofunctionalisation):
    """
    Regarding groups of organisms, the conditions of this neofunctionalisation extend with:
        - The majority of organisms of the descendant group has to contain a gene duplicated enzyme for it (the enzyme or its EC number) to be reported.
    """
    @staticmethod
    def getEnzymesForEC(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                        newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = 80, majorityTotal = None, eValue = defaultEValue) -> Dict[EcNumber, Set[Enzyme]]:
        """
        Returns a Dict of Sets of Enzymes which fulfil the conditions of neofunctionalisation, keyed by the new EC numbers.
        Because the Enzymes are usually from different Organisms, 'majorityPercentage' percent of all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the Enzymes to be returned.
        If 'majorityTotal' is given (not None), majorityPercentage is ignored and the percentage of organisms for a majority is calculated from majorityTotal.
        """
        # check if majority is sane
        if majorityTotal is not None:
            percentage = majorityTotal / descendantOrganismsCount * 100
        else:
            percentage = majorityPercentage
            
        if percentage <= 0 or percentage > 100:
            raise ValueError('Majority percentage is not a sane value (0 < percentage <= 100): ' + str(percentage))
        
        majority = math.ceil((percentage/100) * int( descendantOrganismsCount ) )
        
        # get neofunctionalised enzymes dict
        neofunctionalisedEnzymes = AnyNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, eValue)
        
        # for each new EC number, check if enough organisms have at least one neofunctionalised enzyme associated with this new EC number
        result = dict()
        for ecNumber, enzymesSet in neofunctionalisedEnzymes.items():
            
            organismsCount = dict()
            for enzyme in enzymesSet:
                organismsCount[ enzyme.organismAbbreviation ] = True
            
            # if so, report the EC number.
            if len( organismsCount.keys() ) >= majority:
                result[ ecNumber ] = enzymesSet
        
        return result
    
    @staticmethod
    def getEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                   newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = 80, majorityTotal = None, eValue = defaultEValue) -> Set[Enzyme]:
        """
        Returns a Set of Enzymes which fulfil the conditions of neofunctionalisation.
        Because the Enzymes are usually from different Organisms, 'majorityPercentage' percent of all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the Enzymes to be returned.
        If 'majorityTotal' is given (not None), majorityPercentage is ignored and the percentage of organisms for a majority is calculated from majorityTotal.
        """
        resultDict = MajorityNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage, majorityTotal, eValue)
        resultSets = resultDict.values()
        result = set()
        for resultSet in resultSets:
            result.update( resultSet )
        return result
    
    @staticmethod
    def filterEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                      newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = 80, majorityTotal = None, eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Returns a copy of the descendant's SubstrateEnzymeGraph containing only Enzymes which fulfil the conditions of this neofunctionalisation.
        Because the Enzymes are usually from different Organisms, 'majorityPercentage' percent of all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the Enzymes to be returned.
        If 'majorityTotal' is given (not None), majorityPercentage is ignored and the percentage of organisms for a majority is calculated from majorityTotal.
        """
        graph = descendantEnzymeGraph.copy()
        possibleNeofunctionalisations = MajorityNeofunctionalisation.getEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage, majorityTotal, eValue)
        graph.removeAllEnzymesExcept( possibleNeofunctionalisations )
        return graph
    
    @staticmethod
    def getECs(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
               newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = 80, majorityTotal = None, eValue = defaultEValue) -> Set[EcNumber]:
        """
        Returns a Set of EC numbers from all Enzymes which fulfil the conditions of neofunctionalisation.
        Because the Enzymes are usually from different Organisms, 'majorityPercentage' percent of all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the EC number to be returned.
        If 'majorityTotal' is given (not None), majorityPercentage is ignored and the percentage of organisms for a majority is calculated from majorityTotal.
        """
        resultDict = MajorityNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage, majorityTotal, eValue)
        return set( resultDict.keys() )
    
    @staticmethod
    def filterECs(descendantEcGraph: SubstrateEcGraph,
                  descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                  newECs: Set[EcNumber], descendantOrganismsCount, majorityPercentage = 80, majorityTotal = None, eValue = defaultEValue) -> SubstrateEcGraph:
        """
        Returns a copy of the descendant's SubstrateEcGraph containing only EC numbers which fulfil the condition of this neofunctionalisation.
        Because the Enzymes are usually from different Organisms, 'majorityPercentage' percent of all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the EC number to be returned.
        If 'majorityTotal' is given (not None), majorityPercentage is ignored and the percentage of organisms for a majority is calculated from majorityTotal.
        """
        graph = descendantEcGraph.copy()
        possibleNeofunctionalisations = MajorityNeofunctionalisation.getECs(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage, majorityTotal, eValue)
        graph.removeAllECsExcept( possibleNeofunctionalisations )
        return graph



class ConsensusNeofunctionalisation(Neofunctionalisation):
    """
    Regarding groups of organisms, the conditions of this neofunctionalisation extend with:
        - All organisms of the descendant group has to contain a gene duplicated enzyme for it (the enzyme or its EC number) to be reported.
    """
    @staticmethod
    def getEnzymesForEC(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                        newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> Dict[EcNumber, Set[Enzyme]]:
        """
        Returns a Dict of Sets of Enzymes which fulfil the conditions of neofunctionalisation, keyed by the new EC numbers.
        Because the Enzymes are usually from different Organisms, all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the Enzymes to be returned.
        """
        return MajorityNeofunctionalisation.getEnzymesForEC(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = None, eValue = eValue)
    
    @staticmethod
    def getEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                   newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> Set[Enzyme]:
        """
        Returns a Set of Enzymes which fulfil the conditions of neofunctionalisation.
        Because the Enzymes are usually from different Organisms, all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the Enzymes to be returned.
        """
        return MajorityNeofunctionalisation.getEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = None, eValue = eValue)
    
    @staticmethod
    def filterEnzymes(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                      newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> SubstrateEnzymeGraph:
        """
        Returns a copy of the descendant's SubstrateEnzymeGraph containing only Enzymes which fulfil the conditions of this neofunctionalisation.
        Because the Enzymes are usually from different Organisms, all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the Enzymes to be returned.
        """
        return MajorityNeofunctionalisation.filterEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = None, eValue = eValue)
    
    @staticmethod
    def getECs(descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
               newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> Set[EcNumber]:
        """
        Returns a Set of EC numbers from all Enzymes which fulfil the conditions of neofunctionalisation.
        Because the Enzymes are usually from different Organisms, all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the EC number to be returned.
        """
        return MajorityNeofunctionalisation.getECs(descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = None, eValue = eValue)
    
    @staticmethod
    def filterECs(descendantEcGraph: SubstrateEcGraph,
                  descendantEnzymeGraph: SubstrateEnzymeGraph, geneDuplicationModel: GeneDuplication, 
                  newECs: Set[EcNumber], descendantOrganismsCount, eValue = defaultEValue) -> SubstrateEcGraph:
        """
        Returns a copy of the descendant's SubstrateEcGraph containing only EC numbers which fulfil the condition of this neofunctionalisation.
        Because the Enzymes are usually from different Organisms, all Organisms have to possess a neofunctionalised Enzyme associated with the same EC number, for the EC number to be returned.
        """
        return MajorityNeofunctionalisation.filterECs(descendantEcGraph, descendantEnzymeGraph, geneDuplicationModel, newECs, descendantOrganismsCount, majorityPercentage = 100, majorityTotal = 100, eValue = eValue)

    