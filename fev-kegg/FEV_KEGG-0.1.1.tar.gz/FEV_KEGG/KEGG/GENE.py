from _collections import defaultdict
import string

class Gene(object):
    
    _digit_keeper = defaultdict(type(None))
    _digit_keeper.update({ord(c): c for c in string.digits})
    
    def __init__(self, content):
        """
        Parses a multi-line string from a gene description file into a Gene object.
        """
        
        if isinstance(content, str):
            linesList = content.splitlines()
        
        try:
            # default values
            self.number = None
            self.isProtein = False
            self.organismTnumber = None
            
            self.name = None
            
            self.definition = None
            
            self.ecNumbers = list()
            self.keggOrthologyNames = list()
            self.keggOrthologyIDs = list()
            self.keggOrthologies = list()
            self.isEnzyme = False
            
            self.organismAbbreviation = None
            self.organismName = None
            
            self.pathways = list()
            
            self.positionFrom = None
            self.positionTo = None
            self.positionIsComplement = False
            
            self.aaseqLength = None
            self.aaseq = None
            
            self.ntseqLength = None
            self.ntseq = None
            
            # parse file data
            currentSection = None
            currentContent = None
            
            for line in linesList:
                
                if len(line) == 0 or line[0] == ' ': # section content
                    
                    if currentSection is not None:
                        currentContent.append(line.lstrip())
                    
                else: # section beginning
                    
                    # process previous section
                    lastSection = currentSection
                    
                    if lastSection is not None:
                        if lastSection == 'ENTRY':
                            
                            nextWords = currentContent[0].split()
                            self.number = nextWords[0]
                            self.isProtein = nextWords[1] == 'CDS'
                            self.organismTnumber = nextWords[2]
                            
                        elif lastSection == 'NAME':
                            
                            self.name = currentContent[0]
                        
                        elif lastSection == 'DEFINITION':
                            
                            self.definition = currentContent[0]
                        
                        elif lastSection == 'ORTHOLOGY':
                            
                            for contentLine in currentContent:
                                
                                keggOrthologyID, rest = contentLine.split('  ') # two spaces
                                self.keggOrthologyIDs.append(keggOrthologyID)
                                
                                restSplit = rest.split(' [EC:')
                                if len(restSplit) > 1: # has EC number and long name
                                    
                                    self.isEnzyme = True
                                    ecNumbers = restSplit[1][:-1].split(' ')
                                    longName = restSplit[0]
                                    
                                    self.ecNumbers.extend(ecNumbers) # one space
                                    self.keggOrthologyNames.append(longName)
                                
                                elif len(restSplit) == 1: # has only long name
                                    
                                    ecNumbers = None
                                    longName = restSplit[0]
                                    
                                    self.keggOrthologyNames.append(longName)
                                    
                                else: # has nothing
                                    
                                    ecNumbers = None
                                    longName = None
                                
                                self.keggOrthologies.append( (keggOrthologyID, longName, ecNumbers) )
                        
                        elif lastSection == 'ORGANISM':
                            
                            split = currentContent[0].split('  ') # two spaces
                            self.organismAbbreviation = split[0]
                            self.organismName = split[1]
                        
                        elif lastSection == 'PATHWAY':
                            
                            for contentLine in currentContent:
                                
                                pathwayID, pathwayName = contentLine.split('  ') # two spaces
                                
                                self.pathways.append( (pathwayID, pathwayName) )
                        
                        elif lastSection == 'POSITION':
                            
                            split = currentContent[0].split(':')
                            
                            if len(split) > 1: # there was a colon
                                split = split[1]
                            else:
                                split = split[0]
                            
                            split = split.split('..')
                            if 'complement' in currentContent[0]:
                                self.positionIsComplement = True
                            
                            self.positionFrom = int( split[0].translate(self.__class__._digit_keeper) )
                            self.positionTo = int( split[1].translate(self.__class__._digit_keeper) )
                        
                        elif lastSection == 'AASEQ':
                            
                            self.aaseqLength = int(currentContent[0])
                            self.aaseq = ''.join(currentContent[1:])
                            
                        elif lastSection == 'NTSEQ':
                            
                            self.ntseqLength = int(currentContent[0])
                            self.ntseq = ''.join(currentContent[1:])
                            
                    
                    # begin reading next section
                    split = line.split(maxsplit = 1)
                    
                    firstWord = split[0]
                    if firstWord.startswith('///'):
                        break
                    
                    else:
                        if len(split) > 1:
                            restLine = split[1]
                            currentContent = [restLine]
                        else:
                            currentContent = []
                            
                        currentSection = firstWord
        
        except:
            print( "Error while parsing a gene description into a KEGG.GENE.Gene object:" )
            print( content )
            raise