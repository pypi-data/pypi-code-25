'''
Created on 03 mag 2018

@author: Simone Papandrea
'''

from enum import Enum

class SupInventory(Enum):
  
    WN=('Wordnet')
    NONE=('None')
         
    def __init__(self,name):
        self._name=name

    def __str__(self):
        return self._name
    
    
class SupLanguage(Enum):
  
    EN=("en")
    IT =("it")
    FR=("fr")
                 
    def __init__(self,locale):
        self._language=locale
        
    def __str__(self):
        return str(self._language)
