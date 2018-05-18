'''
Created on 03 mag 2018

@author: Simone Papandrea
'''

from enum import Enum
from supwsd.service import RFService, RFRequest
from supwsd.model import SupSense, SupVersion, SupModel
from supwsd.params import SupLanguage, SupInventory
import json

class SupException(Exception):
    pass

class _Resource(Enum):
  
    SENSES=('senses')
    VERSION=('version')
    MODEL=("model")
    
    def __init__(self,path):
        self._path=path

    def __str__(self):
        return self._path


class SupWSD(object):
  
    MAX_PAYLOAD=500
    SENSE_TAG = "<SENSE>"
        
    class __SupWSD:
        def __init__(self):
            self._service=RFService("https://supwsd-supwsdweb.1d35.starter-us-east-1.openshiftapps.com/supwsdweb/v1/")

        def version(self):
    
            version=None
        
            try:
                result = self._service.get(_Resource.VERSION)

                if not result is None:
                    version = SupVersion[eval(result)]
            
            except Exception as e:
                raise SupException(e)
        
            return version
        
        def model(self):

            model=None
            
            try:
                result = self._service.get(_Resource.MODEL)

                if not result is None:
                    model = SupModel[eval(result)]
            
            except Exception as e:
                raise SupException(e)
        
            return model

        
        def senses(self,text,whole=False):
            return self.__senses(RFRequest(text,SupLanguage.EN,SupInventory.WN,whole))
        
        
        def __senses(self,request):

            senses=None
            
            if request.size() >SupWSD.MAX_PAYLOAD:
                raise ValueError("The text in the input must be at most " + SupWSD.MAX_PAYLOAD + " characters long")
                        
            try:
                result = self._service.post(_Resource.SENSES,{'content':request.to_json()})
                            
                if not result is None:
                    senses=list()
                    for sense in json.loads(result):
                        senses.append(SupSense(sense))
                        
            except Exception as e:
                raise SupException(e)
        
            return senses

    _instance = None
        
    def __new__(cls):
        if not SupWSD._instance:
            SupWSD._instance = SupWSD.__SupWSD()
        return SupWSD._instance
        
    