'''
Created on 03 mag 2018

@author: Simone Papandrea
'''
import requests
import json

class RFRequest(object):

    def __init__(self, content, lang, source, whole=False):
        self._content=content
        self._lang=lang
        self._source=source
        self._all=whole
        
    @property        
    def content(self):
        return self._content
    
    @property
    def language(self):
        return self._lang
    
    @property
    def all(self):
        return self._all
    
    @property
    def source(self):
        return self._source
         
    def size(self):         
        return len(self.content)
    
    def to_json(self):
        return json.dumps({"mContent":self.content,"mLanguage":self.language.name,"mAllSenses":self.all,"mSenseSource":self.source.name})


class RFService(object):

    def __init__(self, service):
        self._url=service       
        
    def post(self, resource, params):
        r = requests.post(self._url+str(resource),data = params,headers=self.__headers(), timeout=30)
        r.raise_for_status()
        return r.text
    
    def get(self, resource,params=None):
        r = requests.get(self._url+str(resource),data = params,headers=self.__headers(), timeout=30)
        r.raise_for_status()
        return r.text

    def __headers(self):
        return {'content-type': 'application/x-www-form-urlencoded',
                "accept-encoding": 'gzip',
                'accept-charset':'UTF8'}