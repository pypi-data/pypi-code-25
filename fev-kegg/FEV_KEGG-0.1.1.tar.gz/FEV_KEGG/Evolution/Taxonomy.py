from enum import Enum
import re

import anytree
from anytree.node.node import Node
from typing import Iterable, List

from FEV_KEGG.KEGG import Database
from FEV_KEGG.KEGG.File import cache


class TaxonType(Enum):
    ROOT = 0
    ORGANISM = 1
    SPECIES = 2
    OTHER = 3

class Taxonomy(object):
    """
    Generic taxonomy of organisms in KEGG.
    """
    def __init__(self, rawLines, isNCBI):
        self.indexOnAbbreviation = dict()
        self.tree = self._parse(rawLines, isNCBI)
    
    def getOrganismNodeByAbbreviation(self, abbreviation: 'eco') -> Node:
        """
        Returns a single Node of TaxonType.ORGANISM with matching abbreviation. None if none can be found.
        """
        return self.indexOnAbbreviation.get(abbreviation, None)
    
    def getOrganismNodesByName(self, name: 'Escherichia') -> List[Node]:
        """
        Returns a list of organism Nodes containing 'name' in their name attribute. None if none found.
        """
        return self.searchNodesByName(name, TaxonType.ORGANISM)
    
    def getOrganismNodesByPath(self, path: 'Gammaproteobacteria/Enterobacterales', exceptPaths: List['Gammaproteobacteria/unclassified'] = None) -> List[Node]:
        """
        Returns a list of organism Nodes containing 'path' in their path. None if none found.
        """
        return self.searchNodesByPath(path, TaxonType.ORGANISM, exceptPaths)
    
    def getOrganismAbbreviations(self, nodes: Iterable[Node]) -> List[str]:
        """
        Returns a list of organism abbreviations from the nodes passed. None if no TaxonType.ORGANISM Node passed.
        """
        if nodes is None:
            return None
        
        abbreviations = []
        for node in nodes:
            
            if node.type == TaxonType.ORGANISM:
                abbreviations.append(node.abbreviation)
        
        if len(abbreviations) == 0:
            abbreviations = None
        
        return abbreviations
    
    def getOrganismAbbreviationsByPath(self, path: 'Gammaproteobacteria/Enterobacterales', exceptPaths: List['Gammaproteobacteria/unclassified'] = None) -> List[str]:
        """
        Returns a list of organism abbreviations from the path passed. None if no valid path passed.
        """
        return self.getOrganismAbbreviations( self.getOrganismNodesByPath(path, exceptPaths) )
    
    def getOrganismAbbreviationsByName(self, name: 'Escherichia') -> List[str]:
        """
        Returns a list of organism abbreviations containing 'name' in their name attribute. None if none found.
        """
        return self.getOrganismAbbreviations( self.getOrganismNodesByName(name) )
    
    def searchNodesByName(self, name: 'Escherichia', taxonType: TaxonType = None) -> List[Node]:
        """
        Returns all Nodes containing 'name' in their name attribute. None if none can be found.
        Only taxons of TaxonType 'taxonType' are returned. If None, all TaxonTypes are considered.
        """
        resultsTuple = anytree.search.findall(self.tree, filter_ = lambda node: (taxonType is node.type or taxonType is None) and name in node.name)
        if len( resultsTuple ) == 0:
            return None
        else:
            return list(resultsTuple)
        
    def searchNodesByPath(self, path: 'Gammaproteobacteria/Enterobacterales', taxonType: TaxonType = None, exceptPaths: 'list of "Gammaproteobacteria/unclassified Bacteria" etc.' = None) -> List[Node]:
        """
        Returns all Nodes containing 'path' in their path. None if none can be found.
        Each path element has to be delimited by a slash '/'.
        Each path element has to match the name of the intermediate taxon exactly.
        
        Only taxons of TaxonType 'taxonType' are returned. If None, all TaxonTypes are considered.
        
        Paths containing any entry of 'exceptPaths' list are not returned.
        Parameter 'exceptPaths' accepts iterables of values and a single value. Strings are treated as single value, not as iterable.
        """
        pathElements = path.split('/')
        
        if path.startswith("/"):
            pathElements[0] = "root"
        
        lastPathElement = pathElements.pop()
        pathElements.reverse()
        
        nodesFound = anytree.search.findall(self.tree, filter_ = lambda node: node.name == lastPathElement)
        
        matchingNodes = []
        
        # find nodes down to the supplied path
        for node in nodesFound:
            
            parent = node.parent
            nodeMatches = True
            
            for lastPathElement in pathElements:
            
                if parent.name != lastPathElement:
                    nodeMatches = False
                    break
                else:
                    parent = parent.parent
            
            if nodeMatches is True:
                matchingNodes.append(node)
        
        # find all children of surviving nodes, filter by TaxonType
        validNodes = []
        for node in matchingNodes:
            descendants = node.descendants
            
            if taxonType is not None:
                for descendant in descendants:
                    if descendant.type == taxonType:
                        validNodes.append(descendant)
            else:
                validNodes = matchingNodes
                validNodes.extend(descendants)
        
        if exceptPaths is None:
            return validNodes
        else:
            if not isinstance(exceptPaths, Iterable) or isinstance(exceptPaths, str):
                exceptPaths = [exceptPaths]
                
            # filter excepted paths
            filteredNodes = []
            for node in validNodes:
                filterNode = False
                for exception in exceptPaths:
                    nodePath = Taxonomy.nodePath2String(node)
                    if exception in nodePath:
                        filterNode = True
                        break
                if filterNode is False:
                    filteredNodes.append(node)
             
            return filteredNodes
    
    @staticmethod
    def nodePath2String(node: Node) -> str:
        return '/'.join([''] + [str(x.name) for x in node.path])
    
    def _parse(self, raw, isNCBI) -> Node:
        
        speciesRegex = re.compile(' \[TAX:[\d]+\]$')
        organismRegex = re.compile('^([a-z]{3,4})  ')
        
        root = Node('root', type = TaxonType.ROOT)
        
        previousNode = root
        previousLevel = 0
        
        for line in raw:
            
            # filter empty line
            if len(line) == 0:
                continue
            
            levelCharacter = line[0]
            
            # filter comments etc. Eveything but line starting with an uppercase letter.
            if not levelCharacter.isupper():
                continue
            
            levelNumber = ord(levelCharacter) - 64
            
            # check if the level is [A-Z]
            if levelNumber < 1 or levelNumber > 26:
                continue
            
            entry = line[1:].strip()
            
            
            # has level changed?
            levelChange = levelNumber - previousLevel
            
            
            # find parent Node
            if levelChange == 0: # same level
                parent = previousNode.parent 
            elif levelChange < 0: # went up in tree
                parent = previousNode.parent
                for _ in range(-levelChange): # for each level we jumped up the tree
                    parent = parent.parent # trace back parents
            else: # went down in tree
                parent = previousNode
            
            
            # is this a species?
            isSpecies = False
            if parent.type is TaxonType.OTHER:
                speciesSplit = speciesRegex.split(entry)
                
                if len(speciesSplit) > 1: # is species
                    isSpecies = True
                    species = speciesSplit[0]
                
                
            # is this an organism?
            isOrganism = False
            if isNCBI is False or parent.type == TaxonType.SPECIES:
                organismSplit = organismRegex.split(entry)
                
                if len(organismSplit) > 1: # is organism
                    isOrganism = True
                    abbreviation = organismSplit[1]
                    name = organismSplit[2]
                elif isNCBI is True: # for NCBI only, this is an incomplete organism (no abbreviation, only Taxon number)
                    continue
                
            
            
            # create new Node
            if isOrganism is True:
                newNode = Node(name, parent, type = TaxonType.ORGANISM, abbreviation = abbreviation)
                self.indexOnAbbreviation[abbreviation] = newNode
            elif isSpecies is True:
                newNode = Node(species, parent, type = TaxonType.SPECIES)
            else:
                newNode = Node(entry, parent, type = TaxonType.OTHER)
            
            # save variables for next round
            previousNode = newNode
            previousLevel = levelNumber
            
        return root



class NCBI(Taxonomy):
    """
    The taxonomy of organisms in KEGG, following the NCBI scheme: http://www.kegg.jp/kegg-bin/get_htext?br08610.keg
    """
    
    @staticmethod
    @cache(folder_path = 'taxonomy/', file_name = 'NCBI_parsed')
    def getTaxonomy() -> Taxonomy:
        """
        Parses raw taxonomy from KEGG into an anytree object.
        """
        raw = Database.getTaxonomyNCBI()
        return Taxonomy(raw, isNCBI = True)


class KEGG(Taxonomy):
    """
    the taxonomy of organisms in KEGG, following KEGG's own scheme: http://www.kegg.jp/kegg-bin/get_htext?br08601.keg
    """
    
    @staticmethod
    @cache(folder_path = 'taxonomy/', file_name = 'KEGG_parsed')
    def getTaxonomy() -> Taxonomy:
        """
        Parses raw taxonomy from KEGG into an anytree object.
        """
        raw = Database.getTaxonomyKEGG()
        return Taxonomy(raw, isNCBI = False)
