from builtins import str
import re
from typing import List, Iterable

from FEV_KEGG.KEGG.GENE import Gene
from FEV_KEGG.Util import Util


class Element(object):
    """
    Generic Element with a unique ID. Comparable by this unique ID.
    """
    def __init__(self, uniqueID: str):
        self.uniqueID = uniqueID
        
    def __str__(self):
        return self.uniqueID
        
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.uniqueID == other.uniqueID
        return False
        
    def __ne__(self, other):
        return not self == other
    
    def __hash__(self):
        return self.uniqueID.__hash__()
    
    def __lt__(self, other):
        return self.uniqueID < other.uniqueID
    
    def __gt__(self, other):
        return self.uniqueID > other.uniqueID
    
    def __le__(self, other):
        return self.uniqueID <= other.uniqueID
    
    def __ge__(self, other):
        return self.uniqueID >= other.uniqueID
    


class DrugIdError(Exception):
    pass

class Substrate(Element):
    """
    Represents a substrate/product of metabolism by compound/glycan ID from KEGG, eg. C01102 or G00160.
    Drug IDs, eg. D08603, raise a ValueError! Use the synonymous Compound ID instead.
    """
    REGEX_PATTERN = re.compile('^C|G[0-9]{5}$')
    
    def __init__(self, keggSubstrateID: 'C01102'):
        
        if keggSubstrateID[0] == 'D':
            raise DrugIdError('Drug IDs are not accepted, as there are usually accompanied by a synonymous Compound ID.')
        
        if self.__class__.REGEX_PATTERN.match(keggSubstrateID) is None: # wrong format
            raise ValueError('Compound/Glycan ID not formatted correctly: ' + keggSubstrateID)
        
        Element.__init__(self, keggSubstrateID)
        self.keggCompoundID = self.uniqueID



class Reaction(Element):
    """
    Represents a reaction of metabolism by reaction ID from KEGG, eg. R01899
    """
    def __init__(self, keggReactionID: 'R01899'):
        Element.__init__(self, keggReactionID)
        self.keggReactionID = self.uniqueID



class Enzyme(Element):
    """
    Represents an enzyme of metabolism. It has exactly one GeneID, which is its unique identifier.
    """
    def __init__(self, organismAbbreviation: 'eco', geneName: 'b0004', name: 'thrC', ecNumberStrings: List[str], description: '(RefSeq) hydrogenase 4, subunit'):
        # build subclasses
        # GeneID
        geneID = GeneID(organismAbbreviation + ':' + geneName)
        # EcNumbers
        ecNumbers = set()
        for ecNumberString in ecNumberStrings:
            ecNumber = EcNumber(ecNumberString)
            ecNumbers.add(ecNumber)
        
        # determine unique ID
        Element.__init__(self, geneID.__str__())
        
        # save object attributes
        self.organismAbbreviation = organismAbbreviation
        self.geneID = geneID
        self.geneName = geneName
        self.name = name
        self.ecNumbers = ecNumbers
        self.description = description
    
    def getEcNumbersString(self):
        """
        Returns EC numbers associated with this enzyme in a string, eg. '1.2.3.4, 2.3.4.5'
        """
        strings = []
        for ecNumber in self.ecNumbers:
            strings.append(ecNumber.__str__())
            
        return ', '.join(strings)
    
    @classmethod
    def fromGene(cls, gene: Gene) -> 'Enzyme':
        return cls(gene.organismAbbreviation, gene.number, gene.name, gene.ecNumbers, gene.definition)
    
    
    def __str__(self):
        return '<' + self.__class__.__name__ + ' ' + self.uniqueID + '>'

class EnzymeComplete(Enzyme):
    """
    Represents an enzyme of metabolism, including all data available from the underlying gene description file.
    Any additional data, in comparison to the parent class Enzyme, can be accessed via the 'gene' property of type KEGG.GENE.Gene.
    """
    def __init__(self, gene: Gene):
        super().__init__(gene.organismAbbreviation, gene.number, gene.name, gene.ecNumbers)
        self.gene = gene
    
    
class EcNumber(Element):
    """
    Represents an enzyme of metabolism by EC number, eg. 4.2.3.1
    """
    WILDCARD = '-'
    REGEX_PATTERN = re.compile('^[1-6]\.(([1-9][0-9]{0,1})|\-)\.(((?<!\-\.)([1-9][0-9]{0,1}))|\-)\.(((?<!\-\.)([1-9][0-9]{0,2}))|\-)$')
    
    def __init__(self, ecNumberString: '4.2.3.1'):
        
        if self.__class__.REGEX_PATTERN.match(ecNumberString) is None: # wrong format
            
            raise ValueError('EC number not formatted correctly: ' + ecNumberString)
        
        # determine unique ID
        Element.__init__(self, ecNumberString)
        
        # save object attributes
        self.ecNumberString = self.uniqueID
        self.ecNumberLevels = self.ecNumberString.split('.')
    
    @classmethod
    def fromArray(cls, ecNumberLevels: Iterable):
        return cls('.'.join(ecNumberLevels))
    
    def contains(self, ecNumber: 'EcNumber'):
        """
        Returns True if an EC number is part of the set of EC numbers defined by wildcard dashes in the levels of this EC number.
        For example 1.2.3.- contains 1.2.3.1 up to 1.2.3.999, but 1.2.3.4 can only contain itself.
        """
        selfLevels = self.ecNumberLevels
        otherLevels = ecNumber.ecNumberLevels
        
        for i in range(0, 4):
            selfNumber = selfLevels[i]
            otherNumber = otherLevels[i]
            if selfNumber != EcNumber.WILDCARD and selfNumber != otherNumber: # current level does not match AND is has no wildcard '-' in this EC number
                return False
        
        return True
    
    
    def matchingLevels(self, ecNumber: 'EcNumber', wildcardMatchesNumber = True):
        """
        Returns the number of consecutive levels that match, if any, starting with the first (leftmost).
        '1.2.3.4'.matchingLevels('1.2.6.7') = 2 because the first two levels match consecutively.
        '1.2.3.4'.matchingLevels('2.2.3.4') = 0 because the very first level does not match.
        This can act as a coarse distance measure for EC numbers.
        If wildcardMatchesNumber == True, a wildcard acts as a sure match: '1.-.-.-'.matchingLevels('1.2.3.4') = 4.
        If wildcardMatchesNumber == False, a wildcard only matches another wildcard.
        """
        matchingLevels = 0
        
        selfLevels = self.ecNumberLevels
        otherLevels = ecNumber.ecNumberLevels
        
        for i in range(0, 4):
            selfNumber = selfLevels[i]
            otherNumber = otherLevels[i]
            
            if wildcardMatchesNumber == True:
                if selfNumber == EcNumber.WILDCARD or otherNumber == EcNumber.WILDCARD or selfNumber == otherNumber: # current level matches OR is a wildcard
                    matchingLevels += 1
                else:
                    return matchingLevels
            else:
                if selfNumber == otherNumber: # current level matches
                    matchingLevels += 1
                else:
                    return matchingLevels
        
        return matchingLevels
    
    def hasWildcard(self):
        """
        If this EC number contains a wildcard (-), returns True, otherwise, returns False.
        """
        for level in self.ecNumberLevels:
            if level == EcNumber.WILDCARD:
                return True
        return False
    
    @staticmethod
    def removeWildcards(ecNumbers: Iterable) -> Iterable:
        """
        Returns a new Iterable of the same type, containing only EC numbers which do NOT have a wildcard (-) anywhere.
        This does not deduplicate EC numbers.
        """
        validECnumbers = []
        for ecNumber in ecNumbers:
            if not ecNumber.hasWildcard():
                validECnumbers.append(ecNumber)
        
        return ecNumbers.__class__(validECnumbers)
    
    @staticmethod
    def insertWildcards(ecNumbers: Iterable, keepLevels = 3, allowHigherWildcards = True, returnSet = True, deduplicateList = False):
        """
        Turns EC numbers without wildcards into EC numbers with wildcards. Returns them in a list, preserving order.
        If 'keepLevels' == 3, turns 1.2.3.4 into 1.2.3.-. Only 1, 2, 3, and 4 are allowed.
        EC numbers already containing wildcards are left unchanged.
        If 'allowHigherWildcards' == False and there is a wildcard in a level above 'keepLevels', i.e. 1.2.3.4 -> 1.2.3.- and 2.3.4.- -> 2.3.4.-, but 3.4.-.- is removed completely.
        If 'returnSet' == True, returns results in a set. Takes precedence over 'deduplicateList', as sets automatically deduplicate.
        If 'deduplicateList' == True, result list is deduplicated before returning, preserving order.
        """
        if not keepLevels in [1, 2, 3, 4]:
            raise ValueError('Can not keep ' + str(keepLevels) + ' levels, there are only 1, 2, 3, or 4.')
        
        filtered = []
        
        for ecNumber in ecNumbers:
            
            levels = ecNumber.ecNumberLevels
            
            filteredLevels = []
            for i in range(0, keepLevels):
                
                level = levels[i]
                
                # check for higher wildcards
                if allowHigherWildcards is False and level == EcNumber.WILDCARD:
                    filteredLevels = None
                    break
                
                else:
                    filteredLevels.append(level)
                
            if filteredLevels is None: # higher wildcard found but disallowed
                continue
            
            else: # pad with wildcards
                for _ in range(4, keepLevels, -1):
                    filteredLevels.append(EcNumber.WILDCARD)
            
            filtered.append( EcNumber.fromArray(filteredLevels) )
        
        if returnSet is True:
            return set( filtered )
            
        if deduplicateList is True:
            filtered = Util.deduplicateList(filtered, preserveOrder = True)
        
        return filtered

    
    
class GeneID(Element):
    """
    Represents am enzyme of metabolism by gene ID, eg. eco:b0004
    """
    REGEX_PATTERN = re.compile('^[a-z]{3,4}:[a-zA-Z0-9_\-\.]+$')
    
    def __init__(self, geneIDString: 'eco:b0004'):
        
        # check input
        if self.__class__.REGEX_PATTERN.match(geneIDString) is None: # wrong format
            raise ValueError('Gene ID not formatted correctly: ' + geneIDString)
        
        # determine unique ID
        Element.__init__(self, geneIDString)
        
        # save object attributes
        self.geneIDString = self.uniqueID
        
    @property
    def organismAbbreviation(self) -> str:
        """
        Returns 'eco' from 'eco:b0004'
        """
        geneIDSplit = self.geneIDString.split(':')
        organismAbbreviation = geneIDSplit[0]
        return organismAbbreviation
    
    @property
    def geneName(self) -> str:
        """
        Returns 'b0004' from 'eco:b0004'
        """
        geneIDSplit = self.geneIDString.split(':')
        geneName = geneIDSplit[1]
        return geneName
    
        
    
class KeggOrthologyID(Element):
    """
    Represents an enzyme of metabolism by KEGG Orthology ID
    """
    REGEX_PATTERN = re.compile('^K[0-9]{5}$')
    
    def __init__(self, keggOrthologyIDString: 'K01733'):
        
        # check input
        if self.__class__.REGEX_PATTERN.match(keggOrthologyIDString) is None: # wrong format
            raise ValueError('KEGG Orthology ID not formatted correctly: ' + keggOrthologyIDString)
        
        # determine unique ID
        Element.__init__(self, keggOrthologyIDString)
        
        # save object attributes
        self.keggOrthologyIDString = self.uniqueID
        