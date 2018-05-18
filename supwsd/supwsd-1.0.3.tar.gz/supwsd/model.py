'''
Created on 03 mag 2018

@author: Simone Papandrea
'''
from enum import Enum

class SupLicense(Enum):
  
    UNRESTRICTED=('UNR')
    CC_BY_NC_SA_30 =('CBNS30')
    OTHER=('OTHER')
         
    def __init__(self,name):
        self._name=name

    def __str__(self):
        return self._name


class SupModel(Enum):
  
    SEMCOR=('SemCor')
    SEMCOR_OMSTI =('SemCor + OMSTI')
    
    def __init__(self,name):
        self._name=name

    def __str__(self):
        return self._name
    

class SupPOS(Enum):    
    NOUN=1,
    VERB=2,
    ADJECTIVE=3,
    ADVERB=4
    

class SupResult(object):
  
    def __init__(self,json):
        self._key=json['mKey']
        self._prob=json['mProbability']
     
    @property       
    def key(self):      
        return self._key
    
    @property
    def prob(self):        
        return self._prob
    
    def __cmp__(self, other):
        return (self.prob > other.prob) - (self.prob< other.prob)
    
    def __eq__(self, other):
        return isinstance(other, SupResult) and self.key == other.key


class SupSource(Enum):
  
    BABELNET=('BabelNet')
    WN =('WordNet')
    
    def __init__(self,name):
        self._name=name

    def __str__(self):
        return self._name
    
    @staticmethod
    def get_license(source):
        
        if source==SupSource.BABELNET:
            return SupLicense.CC_BY_NC_SA_30  
          
        elif source==SupSource.WN:
            return SupLicense.UNRESTRICTED
         
        else:
            return SupLicense.OTHER
       
     
class SupSense(object):
  
    def __init__(self,json):
        self._word=json['mWord']
        self._pos=SupPOS[json['mPOS']]
        self._lemma=json['mLemma']
        self._source=SupSource[json['mSenseSource']]
        self._results=list()
        
        for result in json['mResults']:
            self._results.append(SupResult(result))
        
    @property
    def word(self):
        return self._word
    
    @property
    def pos(self):
        return self._pos
    
    @property
    def lemma(self):
        return self._lemma
    
    @property
    def source(self):        
        return self._source
    
    @property
    def results(self):
        return self._results
    
    def key(self):
        return self.results[0].key
    
    def count(self):
        return len(self.results)
    
    def miss(self):
        return self.key()=='U'
    
    def valid(self):
        return not self.key() is None
        
    def __str__(self):
        return self.key()
    
     
class SupVersion(Enum):
  
    unknown=('unknown')
    V1_0 =('1.0')
    V1_1=('1.1')
    V1_2=('1.2')
    
    def __init__(self,version):
        self._version=version

    def __str__(self):
        return self._version
    
    @staticmethod
    def latest_version():
        return SupVersion.V1_1