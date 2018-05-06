from FEV_KEGG.Graph.SubstrateGraphs import SubstrateEcGraph, SubstrateEnzymeGraph
from FEV_KEGG.Evolution.Taxonomy import NCBI, Taxonomy
from FEV_KEGG.KEGG.Organism import Group 
from FEV_KEGG.Graph.Elements import EcNumber, Enzyme
from typing import Set, Tuple
from FEV_KEGG.Evolution.Events import GeneFunctionAddition, GeneFunctionLoss, GeneFunctionDivergence, GeneFunctionConservation,\
    MajorityNeofunctionalisation, SimpleGeneDuplication

excludeUnclassified = True
excludeMultifunctionalEnzymes = True
defaultMajorityPercentage = 80
defaultMajorityPercentageGeneDuplication = 70
defaultEValue = 1e-15

class Clade(object):
    """
    A clade following NCBI taxonomy.
    """
    
    def __init__(self, ncbiNames: 'e.g. Enterobacter or Proteobacteria/Gammaproteobacteria. Allows list of names, e.g. ["Gammaproteobacteria", "/Archaea"]'):
        """
        A clade in NCBI taxonomy. Exludes any organism with 'unclassified' in its path. Excludes multifunctional enzymes.
        """
        taxonomy = NCBI.getTaxonomy()
        
        if isinstance(ncbiNames, str):
            ncbiNames = [ncbiNames]
            
        self.ncbiNames = ncbiNames
        
        allOrganisms = set()
        for ncbiName in ncbiNames:
            organisms = taxonomy.getOrganismAbbreviationsByPath(ncbiName, exceptPaths=('unclassified' if excludeUnclassified else None))
            if organisms is None or len(organisms) == 0:
                raise ValueError("No clade of this path found: " + ncbiName)
            allOrganisms.update(organisms)
        
        self.group = Group( allOrganisms )
    
    def collectiveMetabolism(self) -> SubstrateEcGraph:
        """
        The Substrate-EC graph representing the collective metabolic network, occuring in any organism of the clade.
        """
        graph = self.group.collectiveEcGraph(noMultifunctional = excludeMultifunctionalEnzymes, addCount = True, keepOnHeap = True)
        graph.name = 'Collective metabolism ECs ' + ' '.join(self.ncbiNames)
        return graph
    
    def collectiveMetabolismEnzymes(self) -> SubstrateEnzymeGraph:
        """
        The Substrate-Enzyme graph representing the collective metabolic network, occuring in any organism of the clade.
        """
    
    def coreMetabolism(self, majorityPercentage = defaultMajorityPercentage) -> SubstrateEcGraph:
        """
        The Substrate-EC graph representing the common metabolic network, shared among all organisms of the clade.
        A path (substrate -> EC -> product) has to occur in 'majorityPercentage' % of the clade's organisms to be included. 
        """
        graph = self.group.majorityEcGraph(majorityPercentage = majorityPercentage, noMultifunctional = excludeMultifunctionalEnzymes, keepOnHeap = True)
        graph.name = 'Core metabolism ECs ' + ' '.join(self.ncbiNames)
        return graph
    
    def coreMetabolismEnzymes(self, majorityPercentage = defaultMajorityPercentage) -> SubstrateEnzymeGraph:
        """
        The Substrate-Enzyme graph representing the common metabolic network, shared among all organisms of the clade.
        Every Enzyme associated with an EC number occuring in core metabolism [see coreMetabolism()] is included, no matter from which organism it stems.
        """
        graph = self.group.collectiveEnzymeGraphByEcMajority(majorityPercentage = majorityPercentage, majorityTotal = None, noMultifunctional = excludeMultifunctionalEnzymes)
        graph.name = 'Core metabolism Enzymes ' + ' '.join(self.ncbiNames)
        return graph
    
    @property
    def organismsCount(self) -> int:
        """
        Returns the number of organisms in the set of organisms of the group of this clade.
        """
        return self.group.organismsCount


class NestedCladePair(object):
    """
    Two clades in NCBI taxonomy, 'child' nested somewhere inside 'parent'.
    """
    
    def __init__(self, parentNCBIname: 'e.g. Proteobacteria/Gammaproteobacteria', childNCBIname: 'e.g. Enterobacter', skipNestedCheck = False):
        """
        'parentNCBIname' and 'childNCBIname' have to be the names or paths of clades as defined by NCBI taxonomy.
        The clade described by 'parentNCBIname' has to contain the clade described by 'childNCBIname', i.e. it is an ancestor.
        
        If 'skipNestedCheck' == True, it is not tested whether child is actually nested within parent.
        Therefore, it would be possible to pass a list of NCBI names to the underlying Clade objects, see Clade.__init__().
        """
        
        taxonomy = NCBI.getTaxonomy()
        
        if skipNestedCheck is False:
            # check if child is really a child of parent
            parentNode = taxonomy.searchNodesByPath(parentNCBIname, exceptPaths=('unclassified' if excludeUnclassified else None))
            if parentNode is None or len(parentNode) == 0:
                raise ValueError("No clade of this path found: " + parentNCBIname)
            else: # only consider first element
                parentNode = parentNode[0]
            
            childNode = taxonomy.searchNodesByPath(childNCBIname, exceptPaths=('unclassified' if excludeUnclassified else None))
            if childNode is None or len(childNode) == 0:
                raise ValueError("No clade of this path found: " + childNCBIname)
            else: # only consider first element
                childNode = childNode[0]
            
            foundParent = False
            for ancestor in childNode.ancestors:
                if Taxonomy.nodePath2String(ancestor) == Taxonomy.nodePath2String(parentNode):
                    foundParent = True
                    break
            
            if foundParent == False:
                raise ValueError("Child is not a descendant of parent.")
        
        self.childClade = Clade(childNCBIname)
        self.childNCBIname = childNCBIname
        
        self.parentClade = Clade(parentNCBIname)
        self.parentNCBIname = parentNCBIname
    
    
    def conservedMetabolism(self, majorityPercentage = defaultMajorityPercentage) -> SubstrateEcGraph:
        """
        The substrate-EC graph representing the metabolic network which stayed the same between the core metabolism of the parent (assumed older) and the core metabolism of the child (assumed younger).
        
        Every substrate-EC edge has to occur in 'majorityPercentage' % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
        The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
        Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless 'majorityPercentage' is consecutively lowered towards 0.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentage)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentage)
        graph = GeneFunctionConservation.getConservedGraph(parentCoreMetabolism, childCoreMetabolism)
        graph.name = 'Conserved metabolism ' + self.parentNCBIname + ' -> ' + self.childNCBIname
        return graph
    
    def conservedMetabolismEnzymes(self, majorityPercentage = defaultMajorityPercentage) -> Tuple[SubstrateEnzymeGraph, SubstrateEnzymeGraph]:
        """
        Returns two substrate-Enzyme graphs in accordance with conservedMetabolism(). The first graph is from the parent clade, the second graph from the child clade.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentage)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentage)
        conservedECs = GeneFunctionConservation.getConservedECs(parentCoreMetabolism, childCoreMetabolism)
        
        parentGraph = self.parentClade.collectiveMetabolismEnzymes().keepEnzymesByEC(conservedECs)
        parentGraph.name = 'Conserved metabolism enzymes *' + self.parentNCBIname + '* -> ' + self.childNCBIname
        
        childGraph = self.childClade.collectiveMetabolismEnzymes().keepEnzymesByEC(conservedECs)
        childGraph.name = 'Conserved metabolism enzymes ' + self.parentNCBIname + ' -> *' + self.childNCBIname + '*'
        
        return (parentGraph, childGraph)
    
    
    def addedMetabolism(self, majorityPercentage = defaultMajorityPercentage) -> SubstrateEcGraph:
        """
        The substrate-EC graph representing the metabolic network which was added to the core metabolism of the parent (assumed older) on the way to the core metabolism of the child (assumed younger).
        
        Every substrate-EC edge has to occur in 'majorityPercentage' % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
        The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
        Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless 'majorityPercentage' is consecutively lowered towards 0.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentage)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentage)
        graph = GeneFunctionAddition.getAddedGraph(parentCoreMetabolism, childCoreMetabolism)
        graph.name = 'Added metabolism ' + self.parentNCBIname + ' -> ' + self.childNCBIname
        return graph
    
    def addedMetabolismEnzymes(self, majorityPercentage = defaultMajorityPercentage) -> Tuple[SubstrateEnzymeGraph, SubstrateEnzymeGraph]:
        """
        Returns two substrate-Enzyme graphs in accordance with addedMetabolism(). The first graph is from the parent clade, the second graph from the child clade.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentage)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentage)
        addedECs = GeneFunctionAddition.getAddedECs(parentCoreMetabolism, childCoreMetabolism)
        
        parentGraph = self.parentClade.collectiveMetabolismEnzymes().keepEnzymesByEC(addedECs)
        parentGraph.name = 'Added metabolism enzymes *' + self.parentNCBIname + '* -> ' + self.childNCBIname
        
        childGraph = self.childClade.collectiveMetabolismEnzymes().keepEnzymesByEC(addedECs)
        childGraph.name = 'Added metabolism enzymes ' + self.parentNCBIname + ' -> *' + self.childNCBIname + '*'
        
        return (parentGraph, childGraph)
    
    
    def lostMetabolism(self, majorityPercentage = defaultMajorityPercentage) -> SubstrateEcGraph:
        """
        The substrate-EC graph representing the metabolic network which got lost from the core metabolism of the parent (assumed older) on the way to the core metabolism of the child (assumed younger).
        
        Every substrate-EC edge has to occur in 'majorityPercentage' % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
        The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
        Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless 'majorityPercentage' is consecutively lowered towards 0.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentage)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentage)        
        graph = GeneFunctionLoss.getLostGraph(parentCoreMetabolism, childCoreMetabolism)
        graph.name = 'Lost metabolism ' + self.parentNCBIname + ' -> ' + self.childNCBIname
        return graph
    
    def lostMetabolismEnzymes(self, majorityPercentage = defaultMajorityPercentage) -> Tuple[SubstrateEnzymeGraph, SubstrateEnzymeGraph]:
        """
        Returns two substrate-Enzyme graphs in accordance with lostMetabolism(). The first graph is from the parent clade, the second graph from the child clade.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentage)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentage)
        lostECs = GeneFunctionLoss.getLostECs(parentCoreMetabolism, childCoreMetabolism)
        
        parentGraph = self.parentClade.collectiveMetabolismEnzymes().keepEnzymesByEC(lostECs)
        parentGraph.name = 'Lost metabolism enzymes *' + self.parentNCBIname + '* -> ' + self.childNCBIname
        
        childGraph = self.childClade.collectiveMetabolismEnzymes().keepEnzymesByEC(lostECs)
        childGraph.name = 'Lost metabolism enzymes ' + self.parentNCBIname + ' -> *' + self.childNCBIname + '*'
        
        return (parentGraph, childGraph)
    
    
    def divergedMetabolism(self, majorityPercentage = defaultMajorityPercentage) -> SubstrateEcGraph:
        """
        The substrate-EC graph representing the metabolic network which changed between the core metabolism of the parent (assumed older) and the core metabolism of the child (assumed younger).
        
        Every substrate-EC edge has to occur in 'majorityPercentage' % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
        The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
        Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless 'majorityPercentage' is consecutively lowered towards 0.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentage)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentage)        
        graph = GeneFunctionDivergence.getDivergedGraph(parentCoreMetabolism, childCoreMetabolism)
        graph.name = 'Diverged metabolism ' + self.parentNCBIname + ' -> ' + self.childNCBIname
        return graph
    
    def divergedMetabolismEnzymes(self, majorityPercentage = defaultMajorityPercentage) -> Tuple[SubstrateEnzymeGraph, SubstrateEnzymeGraph]:
        """
        Returns two substrate-Enzyme graphs in accordance with divergedMetabolism(). The first graph is from the parent clade, the second graph from the child clade.
        """
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentage)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentage)
        divergedECs = GeneFunctionDivergence.getDivergedECs(parentCoreMetabolism, childCoreMetabolism)
        
        parentGraph = self.parentClade.collectiveMetabolismEnzymes().keepEnzymesByEC(divergedECs)
        parentGraph.name = 'Diverged metabolism enzymes *' + self.parentNCBIname + '* -> ' + self.childNCBIname
        
        childGraph = self.childClade.collectiveMetabolismEnzymes().keepEnzymesByEC(divergedECs)
        childGraph.name = 'Diverged metabolism enzymes ' + self.parentNCBIname + ' -> *' + self.childNCBIname + '*'
        
        return (parentGraph, childGraph)
    
    
    
    def neofunctionalisedMetabolism(self, majorityPercentageCoreMetabolism = defaultMajorityPercentage, majorityPercentageGeneDuplication = defaultMajorityPercentageGeneDuplication) -> SubstrateEcGraph:
        """
        The substrate-EC graph representing the metabolic network which was neofunctionalised between the core metabolism of the parent (assumed older) and the core metabolism of the child (assumed younger).
        First calculates addedMetabolism(), then filters results for gene duplication.
        
        Every substrate-EC edge has to occur in 'majorityPercentageCoreMetabolism' % of organisms constituting the clade, to be included in the core metabolism. This is individually true for both parent clade and child clade.
        The parent clade fully includes the child clade, therefore, the occurence of a substrate-EC edge in the child clade's core metabolism counts towards the percentage for the parent clade's core metabolism.
        Meaning: if an EC number does not occur in the child clade's core metabolism, it is unlikely that it will occur in the parent clade's core metabolism, unless 'majorityPercentageCoreMetabolism' is consecutively lowered towards 0.
        
        Every EC number considered for neofunctionalisation has to be associated with enzymes which fulfil the conditions of gene duplication in at least 'majorityPercentageGeneDuplication' % of child clade's organisms.
        A high 'majorityPercentageGeneDuplication' disallows us to detect neofunctionalisations which happened a long time ago, with their genes having diverged significantly; 
        or only recently, with not all organisms of the child clade having picked up the new function, yet.
        However, it also enables us to practically exclude horizontal gene transfer; IF the transferred gene did not already have a sister gene in the receiving organism, with a similar sequence, creating a false positive for gene duplication.
        
        The maximum expectation value (e-value) necessary for a sequence alignment to constitute a "similar sequence" can be changed via Clade.defaultEValue. 
        """
        descendantEnzymeGraph = self.childClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        geneDuplicationModel = SimpleGeneDuplication
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        newECs = GeneFunctionAddition.getAddedECs(parentCoreMetabolism, childCoreMetabolism)
        neofunctionalisedMetabolism = MajorityNeofunctionalisation.filterECs(childCoreMetabolism, descendantEnzymeGraph, geneDuplicationModel, newECs, self.childClade.organismsCount,  majorityPercentage = majorityPercentageGeneDuplication, eValue = defaultEValue)
        neofunctionalisedMetabolism.name = 'Neofunctionalised metabolism ' + self.parentNCBIname + ' -> ' + self.childNCBIname
        return neofunctionalisedMetabolism
        
    def neofunctionalisedMetabolismSet(self, majorityPercentageCoreMetabolism = defaultMajorityPercentage, majorityPercentageGeneDuplication = defaultMajorityPercentageGeneDuplication) -> Set[EcNumber]:
        """
        Same as neofunctionalisedMetabolism().getECs(), but faster.
        """
        descendantEnzymeGraph = self.childClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        geneDuplicationModel = SimpleGeneDuplication
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        newECs = GeneFunctionAddition.getAddedECs(parentCoreMetabolism, childCoreMetabolism)
        neofunctionalisedECs = MajorityNeofunctionalisation.getECs(descendantEnzymeGraph, geneDuplicationModel, newECs, self.childClade.organismsCount,  majorityPercentage = majorityPercentageGeneDuplication, eValue = defaultEValue)
        return neofunctionalisedECs
    
    
    def neofunctionalisedMetabolismEnzymes(self, majorityPercentageCoreMetabolism = defaultMajorityPercentage, majorityPercentageGeneDuplication = defaultMajorityPercentageGeneDuplication) -> SubstrateEnzymeGraph:
        """
        The substrate-Enzyme graph in accordance with neofunctionalisedMetabolism().
        """
        descendantEnzymeGraph = self.childClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        geneDuplicationModel = SimpleGeneDuplication
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        newECs = GeneFunctionAddition.getAddedECs(parentCoreMetabolism, childCoreMetabolism)
        neofunctionalisedMetabolismEnzymes = MajorityNeofunctionalisation.filterEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, self.childClade.organismsCount,  majorityPercentage = majorityPercentageGeneDuplication, eValue = defaultEValue)
        neofunctionalisedMetabolismEnzymes.name = 'Neofunctionalised metabolism enzymes ' + self.parentNCBIname + ' -> ' + self.childNCBIname
        return neofunctionalisedMetabolismEnzymes
    
    def neofunctionalisedMetabolismEnzymesSet(self, majorityPercentageCoreMetabolism = defaultMajorityPercentage, majorityPercentageGeneDuplication = defaultMajorityPercentageGeneDuplication) -> Set[Enzyme]:
        """
        Same as neofunctionalisedMetabolismEnzymes().getECs(), but faster.
        """
        descendantEnzymeGraph = self.childClade.coreMetabolismEnzymes(majorityPercentageCoreMetabolism)
        geneDuplicationModel = SimpleGeneDuplication
        parentCoreMetabolism = self.parentClade.coreMetabolism(majorityPercentageCoreMetabolism)
        childCoreMetabolism = self.childClade.coreMetabolism(majorityPercentageCoreMetabolism)
        newECs = GeneFunctionAddition.getAddedECs(parentCoreMetabolism, childCoreMetabolism)
        neofunctionalisedEnzymes = MajorityNeofunctionalisation.getEnzymes(descendantEnzymeGraph, geneDuplicationModel, newECs, self.childClade.organismsCount,  majorityPercentage = majorityPercentageGeneDuplication, eValue = defaultEValue)
        return neofunctionalisedEnzymes
        
