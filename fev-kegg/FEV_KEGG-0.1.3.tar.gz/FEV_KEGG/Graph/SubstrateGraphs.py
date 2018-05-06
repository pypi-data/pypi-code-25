from FEV_KEGG.lib.Biopython.KEGG.KGML import KGML_pathway
from typing import List, Set, Tuple, Iterable

import FEV_KEGG.Graph.Elements as Elements
from FEV_KEGG.Graph.Models import DirectedMultiGraph
from FEV_KEGG.KEGG import Database
from FEV_KEGG.settings import verbosity as init_verbosity


class SubstrateReactionGraph(DirectedMultiGraph):
    """
    directed multigraph
    node = Elements.Substrate
    edge = Elements.Reaction
    
    Links two Substrates (compound or glycan) with each Reaction they occur in. 
    Substrates have to occur on different sides of the reaction, one being a substrate, the other being a product.
    Reversible reactions will get two Reaction objects with swapped roles of substrate/product.
    There may be other substrates/products in the same reaction, they will be linked with a different Reaction object.
    
    For example A1 + A2 -> B1 + B2 will yield four Reactions: (A1, B1); (A1, B2); (A2, B1); (A2, B2).
    Making this reaction reversible would yield eight Reactions, because each tuple will be swapped to form the other direction.
    """
    
    def __init__(self, underlyingRawGraph = None, pathwaySet = None):
        super().__init__(underlyingRawGraph)
        
        if pathwaySet == None:
            self.pathwaySet = set() # set of pathways objects (KGML_pathway.Pathway) that contributed to this graph
        else:
            self.pathwaySet = pathwaySet.copy()
    
    @property
    def substrateCounts(self):
        return self.nodeCounts
    
    @property
    def reactionCounts(self):
        return self.edgeElementCounts
    
    @staticmethod
    def fromPathway(pathway: Set[KGML_pathway.Pathway]):
        """
        Returns a substrate-reaction graph from a single pathway, or from a set of pathways.
        """
        if isinstance(pathway, KGML_pathway.Pathway): # only single pathway given
            return Conversion.KeggPathway2SubstrateReactionGraph(pathway)
        else: # multiple pathways given
            return Conversion.KeggPathwaySet2SubstrateReactionGraph(pathway)
    
    def addReaction(self, substrate: Elements.Substrate, product: Elements.Substrate, reaction: Elements.Reaction, isReversible: bool = False):
        """
        Adds a Reaction 'reaction' between Substrates 'substrate' and 'product'. Only in this direction, unless isReversible == True, the in both directions. Automatically adds Substrate nodes, if not already in the graph.
        """
        super().addEdge(substrate, product, reaction, isReversible) # automatically creates node, if not already present
        
    def getUnidirectionalReactions(self) -> Set[Elements.Reaction]:
        """
        Return a set of all reactions that have only one direction.
        """
        return self.getUnidirectionalEdgesElements()
    
    def getReactions(self) -> Set[Elements.Reaction]:
        """
        Returns a set of all reactions.
        """
        return self.getEdgesElements()
    
    def copy(self, underlyingRawGraph = None):
        """
        Returns a shallow copy.
        However, some attributes are explicitly copied (although each attribute might itself be shallowly copied):
        .underlyingRawGraph
        .name
        .pathwaySet
        """
        copy = super().copy(underlyingRawGraph)
        copy.pathwaySet = self.pathwaySet.copy()
        
        return copy
        

class SubstrateGeneGraph(DirectedMultiGraph):
    """
    directed multigraph
    node = Elements.Substrate
    edge = Elements.GeneID
    
    Replaces Reactions with their associated GeneIDs. Splits Reactions with several GeneIDs. Deduplicates Reactions with the same GeneID.
    """
    
    @property
    def substrateCounts(self):
        return self.nodeCounts
    
    @property
    def geneCounts(self):
        return self.edgeElementCounts
    
    @staticmethod
    def fromSubstrateReactionGraph(speciesSubstrateReactionGraph: SubstrateReactionGraph):
        return Conversion.SubstrateReactionGraph2SubstrateGeneGraph(speciesSubstrateReactionGraph)
    
    def addGene(self, substrate: Elements.Substrate, product: Elements.Substrate, geneID: Elements.GeneID, isReversible: bool = False):
        """
        Adds an GeneID 'geneID' between Substrates 'substrate' and 'product'. Only in this direction, unless isReversible == True, the in both directions. Automatically adds Substrate nodes, if not already in the graph.
        """
        super().addEdge(substrate, product, geneID, isReversible) # automatically creates node, if not already present
    
    def getGenes(self) -> Set[Elements.GeneID]:
        """
        Returns a set of all gene IDs.
        """
        return self.getEdgesElements()
    
    def getUnidirectionalGenes(self) -> Set[Elements.GeneID]:
        """
        Return a set of all gene IDs that have only one direction.
        """
        return self.getUnidirectionalEdgesElements()
    
    def getMultifunctionalGeneEdges(self) -> List[Tuple]:
        """
        Returns a list of all edge tuples with a gene associated with more than one EC number. Parses Database, this is expensive!
        """
        multifunctionalEdgeList = []
        edgeList = self.getEdges()
        
        geneIDs = [x for _,_,x in edgeList]
        geneDict = Database.getGeneBulk(geneIDs)            
            
        for edge in edgeList:
            _, _, element = edge
            
            gene = geneDict.get(element.geneIDString, None)
            
            if gene is None: # should not happen, but might
                continue
            
            ecNumbersList = Elements.Enzyme.fromGene(gene).ecNumbers
            
            if len(ecNumbersList) > 1:
                multifunctionalEdgeList.append(edge)
        
        return multifunctionalEdgeList
    
    def getMultifunctionalGenes(self) -> Set[Elements.GeneID]:
        """
        Returns a set of all gene IDs associated with more than one EC number. Parses Database, this is expensive!
        """
        genes = set()
        edges = self.getMultifunctionalGeneEdges()
        for edge in edges:
            _, _, gene = edge
            genes.add(gene)
        
        return genes
        
    def removeMultifunctionalGenes(self):
        """
        Removes genes associated with more than one EC number. Parses Database, this is expensive!
        You may want to removeIsolatedNodes() afterwards, to remove nodes that now have no edge.
        """
        multifunctionalEdges = self.getMultifunctionalGeneEdges()
        super().removeEdges(multifunctionalEdges)


class SubstrateEnzymeGraph(DirectedMultiGraph):
    """
    directed multigraph
    node = Elements.Substrate
    edge = Elements.Enzyme (unique by GeneID)
    
    Replaces GeneID with their associated Enzyme object. Automatically parses genes from Database, this is expensive!
    """
    
    def __init__(self, underlyingRawGraph: 'implementationGraph' = None):
        DirectedMultiGraph.__init__(self, underlyingRawGraph)
        self.indexOnEC = dict() # EcNumber -> set{Enzyme, Enzyme, ...}
        self.indexOnGeneID = dict() # GeneID -> Enzyme
    
    @property
    def substrateCounts(self):
        return self.nodeCounts
    
    @property
    def enzymeCounts(self):
        return self.edgeElementCounts
    
    # override parent class methods, to keep index up-to-date
    def addEdge(self, node1:Elements.Element, node2:Elements.Element, key:Elements.Element, isReversible:bool=False):
        if isinstance(key, Elements.Enzyme):
            self.addEnzyme(node1, node2, key, isReversible)
        else:
            super().addEdge(node1, node2, key, isReversible)
    
    def addEdges(self, edges: List[Tuple[Elements.Element, Elements.Element, Elements.Element]]):
        for substrate, product, key in edges:
            if isinstance(key, Elements.Enzyme):
                self.addEnzyme(substrate, product, key, isReversible = False)
            else:
                super().addEdge(substrate, product, key, isReversible = False)
    
    def removeEdge(self, node1:Elements.Element, node2:Elements.Element, key:Elements.Element, bothDirections:bool=False):
        if isinstance(key, Elements.Enzyme):
            self.removeEnzymeEdge(node1, node2, key, bothDirections)
        else:
            super().removeEdge(node1, node2, key, bothDirections)
        
    def removeEdges(self, edges:List[Tuple]):
        self.removeEnzymeEdges(edges)
        
    def removeEdgesByElement(self, elements:Iterable[Elements.Element]):
        self.removeEnzymes(elements)
    
    
    @staticmethod
    def fromSubstrateGeneGraph(substrateGeneGraph: SubstrateGeneGraph):
        return Conversion.SubstrateGeneGraph2SubstrateEnzymeGraph(substrateGeneGraph)
    
    def getEnzymes(self) -> Set[Elements.Enzyme]:
        """
        Returns a set of all enzymes.
        """
        return self.getEdgesElements()
    
    def addEnzyme(self, substrate: Elements.Substrate, product: Elements.Substrate, enzyme: Elements.Enzyme, isReversible: bool = False):
        """
        Adds an Enzyme 'enzyme' between Substrates 'substrate' and 'product'. Only in this direction, unless isReversible == True. Automatically adds Substrate nodes, if not already in the graph.
        """
        super().addEdge(substrate, product, enzyme, isReversible) # automatically creates node, if not already present
        
        # add Enzyme to EC index
        for ecNumber in enzyme.ecNumbers:
            enzymeSet = self.indexOnEC.get(ecNumber, None)
            if enzymeSet is None:
                newEnzymeSet = set()
                newEnzymeSet.add(enzyme)
                self.indexOnEC[ecNumber] = newEnzymeSet
            else:
                enzymeSet.add(enzyme)
                
        # add Enzyme to GeneID index
        self.indexOnGeneID[enzyme.geneID] = enzyme
    
    def removeEnzymes(self, enzymes: Iterable[Elements.Enzyme]):
        """
        Removes all occurences of the Enzymes in the Iterable 'enzymes'.
        """
        super().removeEdgesByElement(enzymes)
        
        for enzyme in enzymes:
            # remove Enzyme from EC index
            for ecNumber in enzyme.ecNumbers:
                enzymeSet = self.indexOnEC.get(ecNumber, None)
                if enzymeSet is not None:
                    enzymeSet.discard(enzyme)
                    if len( enzymeSet ) == 0: # enzyme set is now empty, remove it completely
                        del self.indexOnEC[ecNumber]
            
            # remove Enzyme from GeneID index
            if self.indexOnGeneID.get(enzyme.geneID, None) is not None:
                del self.indexOnGeneID[enzyme.geneID]
    
    def removeAllEnzymesExcept(self, enzymesToKeep: Iterable[Elements.Enzyme]):
        """
        Removes all Enzymes not in the specified Iterable.
        """
        enzymesToKeepSet = set()
        enzymesToKeepSet.update(enzymesToKeep)
        enzymesToRemove = self.getEnzymes()
        enzymesToRemove.difference_update(enzymesToKeepSet)
        self.removeEnzymes(enzymesToRemove)
    
    def removeEnzymeEdge(self, substrate: Elements.Substrate, product: Elements.Substrate, enzyme: Elements.Enzyme, bothDirections: bool = False):
        """
        Removes an Enzyme 'enzyme' between Substrates 'substrate' and 'product'. Only in this direction, unless bothDirections == True. Does not remove Substrate nodes.
        """
        super().removeEdge(substrate, product, enzyme, bothDirections)
        
        # remove Enzyme from EC index
        for ecNumber in enzyme.ecNumbers:
            enzymeSet = self.indexOnEC.get(ecNumber, None)
            if enzymeSet is not None:
                enzymeSet.discard(enzyme)
                if len( enzymeSet ) == 0: # enzyme set is now empty, remove it completely
                    del self.indexOnEC[ecNumber]
        
        # remove Enzyme from GeneID index
        if self.indexOnGeneID.get(enzyme.geneID, None) is not None:
            del self.indexOnGeneID[enzyme.geneID]
    
    def removeEnzymeEdges(self, enzymeEdges: List[Tuple]):
        """
        Removes all Enzymes in the specified list. Each list entry has to be of type Tuple(substrate, product, enzyme).
        If an edge to be removed does not exist, the next edge will be tried, without any error message.
        """
        for enzymeEdge in enzymeEdges:
            substrate, product, enzyme = enzymeEdge
            self.removeEnzymeEdge(substrate, product, enzyme, bothDirections = False)
    
    def getMultifunctionalEnzymeEdges(self) -> List[Tuple]:
        """
        Returns a list of all edge tuples with an enzyme associated with more than one EC number.
        """
        multifunctionalEdgeList = []
        edgeList = self.getEdges()
        for edge in edgeList:
            _, _, element = edge
            
            ecNumbersList = element.ecNumbers
            
            if len(ecNumbersList) > 1:
                multifunctionalEdgeList.append(edge)
        
        return multifunctionalEdgeList
    
    def getMultifunctionalEnzymes(self) -> Set[Elements.Enzyme]:
        """
        Returns a set of all enzymes associated with more than one EC number.
        """
        enzymes = set()
        edges = self.getMultifunctionalEnzymeEdges()
        for edge in edges:
            _, _, enzyme = edge
            enzymes.add(enzyme)
        
        return enzymes
        
    def removeMultifunctionalEnzymes(self):
        """
        Removes enzymes associated with more than one EC number.
        You may want to removeIsolatedNodes() afterwards, to remove nodes that now have no edge.
        """
        multifunctionalEdges = self.getMultifunctionalEnzymeEdges()
        self.removeEnzymeEdges(multifunctionalEdges)
        
    def getEnzymesForEcNumber(self, ecNumber: Elements.EcNumber) -> Set[Elements.Enzyme]:
        """
        Returns a set of Elements.Enzymes associated with the EC number in the ecNumber parameter.
        If there is no such EC number, returns an empty set.
        """
        return self.indexOnEC.get(ecNumber, set())
    
    def getGeneIDsForEcNumber(self, ecNumber: Elements.EcNumber) -> Set[Elements.GeneID]:
        """
        Returns a set of Elements.GeneIDs associated with the EC number in the ecNumber parameter.
        If there is no such EC number, returns an empty set.
        """
        enzymes = self.getEnzymesForEcNumber(ecNumber)
        
        geneIDs = set()
        for enzyme in enzymes:
            geneID = enzyme.geneID
            geneIDs.add(geneID)
        
        return geneIDs
    
    def getEnzymeForGeneID(self, geneID: Elements.GeneID) -> Elements.Enzyme:
        """
        Returns the Elements.Enzyme in this graph identified by the given GeneID.
        If there is no such GeneID, returns None.
        """
        return self.indexOnGeneID.get(geneID, None)
    
    def removeEnzymesByEC(self, ecNumbers: Iterable[Elements.EcNumber], keepInstead = False):
        """
        Removes all enzymes associated with the passed EC numbers.
        If keepInstead == True, remove all enzymes except the ones associated with the passed EC numbers.
        """
        enzymesOfInterest = []
        
        for ecNumber in ecNumbers:
            foundEnzymes = self.getEnzymesForEcNumber( ecNumber )
            enzymesOfInterest.extend( foundEnzymes )
            
        enzymesOfInterest = set( enzymesOfInterest )
        
        if keepInstead == True:
            self.removeAllEnzymesExcept(enzymesOfInterest)
        else:
            self.removeEnzymes(enzymesOfInterest)
    
    def keepEnzymesByEC(self, ecNumbers: Iterable[Elements.EcNumber]):
        """
        Keep all enzymes associated with the passed EC numbers, remove the rest.
        """
        return self.removeEnzymesByEC(ecNumbers, keepInstead = True)
    


class SubstrateEcGraph(DirectedMultiGraph):
    """
    directed multigraph
    node = Elements.Substrate
    edge = Elements.EcNumber
    
    Replaces GeneIDs/Enzyme with their EcNumber. Splits GeneIDs with several EC numbers. Deduplicates GeneIDs with the same EC number.
    """
    @property
    def substrateCounts(self):
        return self.nodeCounts
    
    @property
    def ecCounts(self):
        return self.edgeElementCounts
    
    @staticmethod
    def fromSubstrateGeneGraph(substrateGeneGraph: SubstrateGeneGraph):
        return Conversion.SubstrateGeneGraph2SubstrateEcGraph(substrateGeneGraph)
    
    @staticmethod
    def fromSubstrateEnzymeGraph(substrateEnzymeGraph: SubstrateEnzymeGraph):
        return Conversion.SubstrateEnzymeGraph2SubstrateEcGraph(substrateEnzymeGraph)
        
    def getECs(self) -> Set[Elements.EcNumber]:
        """
        Returns a set of all EC numbers.
        """
        return self.getEdgesElements()
    
    def addEC(self, substrate: Elements.Substrate, product: Elements.Substrate, ecNumber: Elements.EcNumber, isReversible: bool = False):
        """
        Adds an EcNumber 'ecNumber' between Substrates 'substrate' and 'product'. Only in this direction, unless isReversible == True, the in both directions. Automatically adds Substrate nodes, if not already in the graph.
        """
        super().addEdge(substrate, product, ecNumber, isReversible) # automatically creates node, if not already present
    
    def removeEC(self, ecNumber: Elements.EcNumber):
        """
        Removes all occurences of an EcNumber 'ecNumber'. Does not remove Substrate nodes.
        """
        super().removeEdgesByElement([ecNumber])
        
    def removeECs(self, ecNumbers: Iterable[Elements.EcNumber]):
        """
        Removes all occurences of an EcNumber 'ecNumber'. Does not remove Substrate nodes.
        """
        super().removeEdgesByElement(ecNumbers)
    
    def removeEcEdge(self, substrate: Elements.Substrate, product: Elements.Substrate, ecNumber: Elements.EcNumber, bothDirections: bool = False):
        """
        Removes an EcNumber 'ecNumber' between Substrates 'substrate' and 'product'. Only in this direction, unless bothDirections == True. Does not remove Substrate nodes.
        """
        super().removeEdge(substrate, product, ecNumber, bothDirections)
    
    def removeEcEdges(self, ecEdges: List[Tuple]):
        """
        Removes all EcNumbers in the specified list. Each list entry has to be of type Tuple(substrate, product, ecNumber).
        If an edge to be removed does not exist, the next edge will be tried, without any error message.
        """
        for ecEdge in ecEdges:
            substrate, product, ecNumber = ecEdge
            self.removeEcEdge(substrate, product, ecNumber, bothDirections = False)
    
    def removeAllECsExcept(self, ecToKeep: Iterable[Elements.EcNumber]):
        """
        Removes all EcNumbers not in the specified Iterable.
        """
        ecToKeepSet = set()
        ecToKeepSet.update(ecToKeep)
        ecToRemove = self.getECs()
        ecToRemove.difference_update(ecToKeepSet)
        self.removeECs(ecToRemove)
    
    def getUnidirectionalEcNumbers(self) -> Set[Elements.EcNumber]:
        """
        Return a set of all ec numbers that have only one direction.
        """
        return self.getUnidirectionalEdgesElements()
    
    def getPartialEcNumberEdges(self) -> List[Tuple]:
        """
        Returns a list of all edge tuples with an EC number with less than the full four EC levels, eg. '4.1.2.-'. Even though the type list does not enforce it, this should never return duplicates.
        """
        partialEdgeList = []
        edgeList = self.getEdges()
        for edge in edgeList:
            _, _, element = edge
            
            # split EC number in its four levels
            levels = element.ecNumberString.split('.')
            
            # check if there are exactly four levels
            if len(levels) != 4:
                partialEdgeList.append(edge)
                continue
            
            # check if each level is a positive integer
            for level in levels:
                if level.isdigit() == False:
                    partialEdgeList.append(edge)
                    break # prevents counting an edge multiple times if it has multiple non-integer levels
        
        return partialEdgeList
    
    def getPartialEcNumbers(self) -> Set[Elements.EcNumber]:
        """
        Returns a set of all EC numbers with less than the full four EC levels, eg. '4.1.2.-'.
        """
        paralog_ecNumbers = set()
        edges = self.getPartialEcNumberEdges()
        for edge in edges:
            _, _, ecNumber = edge
            paralog_ecNumbers.add(ecNumber)
        
        return paralog_ecNumbers
    
    def removePartialEcNumbers(self):
        """
        Removes EcNumber edges with less than the full four EC levels, eg. '4.1.2.-'.
        You may want to removeIsolatedNodes() afterwards, to remove nodes that now have no edge.
        """
        partialEdges = self.getPartialEcNumberEdges()
        super().removeEdges(partialEdges)
    











class Conversion:
    @staticmethod
    def KeggPathway2SubstrateReactionGraph(pathway: KGML_pathway.Pathway, localVerbosity = init_verbosity) -> SubstrateReactionGraph:
        """
        Converts an organism's pathway into a format from which a SubstrateReactionGraph can then be built and returned. Pathway pathwayName is saved in graph's pathwayName, eg. 'eco01100'.
        """
        # create empty graph
        graph = SubstrateReactionGraph()
        graph.pathwaySet.add(pathway)
        pathwayName = pathway.name.replace('path:', '')
        graph.name = 'Substrate-Reaction ' + pathwayName
        
        # parse reaction tags from pathway
        reactionList = pathway.reactions
        
        for reaction in reactionList:
            
            # decode a single reaction tag
            isReversible = reaction.type == 'reversible'
            substrateIDList = reaction.substrates
            productIDList = reaction.products
            reactionIDList = reaction.name.split()
            
            # build graph Elements
            substrateList = []
            productList = []
            
            # build Elements.Substrate
            for substrateID in substrateIDList:
                substrateNameList = substrateID.name.split(' ')
                for substrateNameListEntry in substrateNameList:
                    substrateName = substrateNameListEntry.split(':', 1)[1]
                    try:
                        substrate = Elements.Substrate(substrateName)
                    except Elements.DrugIdError: # ignore Drug IDs
                        continue
                    substrateList.append(substrate)
                
            for productID in productIDList:
                productNameList = productID.name.split(' ')
                for productNameListEntry in productNameList:
                    productName = productNameListEntry.split(':', 1)[1]
                    try:
                        product = Elements.Substrate(productName)
                    except Elements.DrugIdError: # ignore Drug IDs
                        continue
                    productList.append(product)
                
            # build Elements.Reaction
            for reactionID in reactionIDList:
                reactionName = reactionID.split(':', 1)[1]
                reaction = Elements.Reaction(reactionName)
                
                # fill graph with these new elements. Each substrate is connected pair-wise to every product. 
                for substrate in substrateList:
                    for product in productList:
                        graph.addReaction(substrate, product, reaction, isReversible) # automatically creates node, if not already present. In both directions, if reversible.
                        
        if localVerbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph

    @classmethod
    def KeggPathwaySet2SubstrateReactionGraph(cls, pathways: Set[KGML_pathway.Pathway], localVerbosity = init_verbosity, name = None) -> SubstrateReactionGraph:
        """
        Combines several pathways of an organism into one SubstrateReactionGraph. Deduplicates nodes and edges. Name of the graph is the names of the pathways, joined by a space, eg. 'eco00260 eco01100'.
        """
        newPathwaySet = set()
        #pathwayNameList = []
        graphs = []
        for pathway in pathways:
            graph = cls.KeggPathway2SubstrateReactionGraph(pathway, localVerbosity = 0)
            newPathwaySet.update(graph.pathwaySet)
            #pathwayNameList.append(pathway.name.replace('path:', ''))
            graphs.append(graph)
        
        if name is None:
            newName = 'Substrate-Reaction multiple pathways'
        else:
            newName = 'Substrate-Reaction ' + name #+ ' '.join(pathwayNameList)
        
        graph = SubstrateReactionGraph.composeAll(graphs=graphs, name=newName, pathwaySet=newPathwaySet)
        
        if localVerbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
    
    @staticmethod
    def SubstrateReactionGraph2SubstrateGeneGraph(speciesSubstrateReactionGraph: SubstrateReactionGraph) -> SubstrateGeneGraph:
        """
        Converts a substrate-reaction graph into a substrate-gene graph. Uses pathway information embedded into the graph object.
        """
        # shallow-copy old graph to new graph
        graph = SubstrateGeneGraph(speciesSubstrateReactionGraph.underlyingRawGraph)
        graph.name = 'Substrate-Gene ' + speciesSubstrateReactionGraph.name.split('ubstrate-Reaction ', maxsplit=1)[1]
        
        # create dict of replacements: reaction -> {genes}
        replacementDict = dict()
        
        # for each embedded pathway, get list of genes
        for pathway in speciesSubstrateReactionGraph.pathwaySet:
            geneEntryList = pathway.genes
            
            # for each gene, get reactions in which it is involved
            for geneEntry in geneEntryList:
                reactionIDList = geneEntry.reaction.split()
                if len(reactionIDList) > 0: # filter genes not associated with any reaction
                    geneIDList = geneEntry.name.split()
                    
                    # replace each reaction with its associated genes
                    for reactionID in reactionIDList:
                        reactionName = reactionID.split(':', 1)[1]
                        reaction = Elements.Reaction(reactionName)
                        
                        # save associated genes in a set
                        geneSet = set()
                        for geneID in geneIDList:
                            gene = Elements.GeneID(geneID)
                            geneSet.add(gene)
                        
                        # update the replacement dict for the current reaction, adding the newly created gene set
                        replacementSet = replacementDict.get(reaction, None)
                        if replacementSet == None or replacementSet.__class__ != set:
                            replacementSet = set()
                        replacementSet.update(geneSet)
                        replacementDict[reaction] = replacementSet
        
        # get list of all reaction edges. Copy edge list to prevent changes in-place, which would NOT work
        edgeList = list(graph.getEdges())
            
        # replace reaction edges with gene edges, using replacement dict
        for edge in edgeList:
            substrate, product, reaction = edge
            
            # delete old edge
            graph.removeEdge(substrate, product, reaction, False)
            
            # add new edges, according to replacement dict
            replacementSet = replacementDict[reaction]
            for gene in replacementSet:
                graph.addGene(substrate, product, gene, False)
        
        if init_verbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
    
    @staticmethod
    def SubstrateGeneGraph2SubstrateEcGraph(substrateGeneGraph: SubstrateGeneGraph) -> SubstrateEcGraph:
        """
        Converts a substrate-gene graph into a substrate-ec graph. 
        Skips the substrate-enzyme step. Still parses genes from Database, this is expensive!
        """
        # shallow-copy old graph to new graph
        graph = SubstrateEcGraph(substrateGeneGraph.underlyingRawGraph)
        graph.name = 'Substrate-Ec ' + substrateGeneGraph.name.split('ubstrate-Gene ', maxsplit=1)[1]
        
        # create dict of replacements: gene -> {ec}
        replacementDict = dict()
        
        # get list of all gene edges. Copy edge list to prevent changes in-place, which would NOT work
        edgeList = list(graph.getEdges())
        
        # populate set of genes, because there are many genes used in more than one edge
        geneSet = set()
        for edge in edgeList:
            _, _, gene = edge
            geneSet.add(gene)
            
        # for each gene, retrieve ec numbers, only once per gene because this is expensive
        geneDict = Database.getGeneBulk(geneSet)
        for geneID, gene in geneDict.items():
            
            ecNumbersList = Elements.Enzyme.fromGene(gene).ecNumbers
            
            # fill replacement dict
            if ecNumbersList is not None and len(ecNumbersList) > 0:
                replacementDict[geneID] = ecNumbersList
            else:
                replacementDict[geneID] = None
                
        # replace gene edges with ec edges, using replacement dict
        for edge in edgeList:
            substrate, product, geneID = edge
            
            # delete old edge
            graph.removeEdge(substrate, product, geneID, False)
            
            # add new edges, according to replacement dict
            replacementList = replacementDict[geneID]
            if replacementList is not None:
                for ecNumber in replacementList:
                    graph.addEC(substrate, product, ecNumber, False)
        
        if init_verbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
    
    @staticmethod
    def SubstrateGeneGraph2SubstrateEnzymeGraph(substrateGeneGraph: SubstrateGeneGraph, noMultifunctional = False) -> SubstrateEnzymeGraph:
        """
        Converts a substrate-gene graph into a substrate-enzyme graph. Parses genes from Database, this is expensive! Each unique gene ID is mapped to the same unique enzyme, because enzymes are unique by their gene ID.
        """
        # shallow-copy old graph to new graph
        graph = SubstrateEnzymeGraph(substrateGeneGraph.underlyingRawGraph)
        graph.name = 'Substrate-Enzyme ' + substrateGeneGraph.name.split('ubstrate-Gene ', maxsplit=1)[1]
        
        # create dict of replacements: gene -> enzyme
        replacementDict = dict()
        
        # get list of all gene edges. Copy edge list to prevent changes in-place, which would NOT work
        edgeList = list(graph.getEdges())
        
        # populate set of genes, because there are many genes used in more than one edge
        geneSet = set()
        for edge in edgeList:
            _, _, gene = edge
            geneSet.add(gene)
            
        # for each gene, build enzyme object, only once per gene because this is expensive
        geneDict = Database.getGeneBulk(geneSet)
        for geneID, gene in geneDict.items():

            enzyme = Elements.Enzyme.fromGene(gene)
        
            # fill replacement dict
            if enzyme is not None:
                if noMultifunctional is True: # if required, ignore enzymes with multiple EC numbers
                    if len(enzyme.ecNumbers) > 1:
                        continue
                replacementDict[geneID] = enzyme
                
        # replace gene edges with enzyme edges, using replacement dict
        for edge in edgeList:
            substrate, product, geneID = edge
            
            # delete old edge
            graph.removeEdge(substrate, product, geneID, False)
            
            # add new edges, according to replacement dict
            enzyme = replacementDict.get(geneID, None)
            if enzyme is not None:
                graph.addEnzyme(substrate, product, enzyme, False)
        
        if init_verbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
        
    @staticmethod
    def SubstrateEnzymeGraph2SubstrateEcGraph(substrateEnzymeGraph: SubstrateEnzymeGraph) -> SubstrateEcGraph:
        """
        Converts a substrate-enzyme graph into a substrate-ec graph.
        """        
        # shallow-copy old graph to new graph
        graph = SubstrateEcGraph(substrateEnzymeGraph.underlyingRawGraph)
        graph.name = 'Substrate-Ec ' + substrateEnzymeGraph.name.split('ubstrate-Enzyme ', maxsplit=1)[1]
        
        # get list of all enzyme edges. Copy edge list to prevent changes in-place, which would NOT work
        edgeList = list(graph.getEdges())
        
        # replace enzyme edges with ec edges, duplicates will be ignored
        for edge in edgeList:
            substrate, product, enzyme = edge
            
            # delete old edge
            graph.removeEdge(substrate, product, enzyme, False)
            
            # add new edges
            replacementList = enzyme.ecNumbers
            if replacementList is not None:
                for ecNumber in replacementList:
                    graph.addEC(substrate, product, ecNumber, False)
        
        if init_verbosity >= 2:
            print('calculated ' + graph.name)
        
        return graph
