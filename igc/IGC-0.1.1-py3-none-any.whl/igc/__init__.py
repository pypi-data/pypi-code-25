
# coding: utf-8

import requests, json, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from enum import Enum

class igc(object):

    session = requests.Session()
    session.verify = False
    assetCache = dict()
    
    class Type(Enum):
        category = 'category'
        term     = 'term'
        
    def __init__(self, domain , password, username, port, protocol):
        if port == 443:
            self.url = protocol+'://'+domain
        else:
            self.url = protocol+'://'+domain+':'+str(port)
        self.session.auth=(username, password)

    def getAsset(self, id, property = '', useCache = True): # type: term, category
        if self.assetCache.get(id+property) == None or useCache == False:
            url = self.url+'/ibm/iis/igc-rest/v1/assets/'+id+'/'+property  #+ "?pageSize=100000"
            resp = self.session.get(url=url)
            self.assetCache[id+property] = resp.json()
        return self.assetCache[id+property]
                
    def searchForId(self, name, type = Type.term): # type: term, category
        headers = {'content-type': 'application/json'}
        url = self.url+'/ibm/iis/igc-rest/v1/search'
        body = {
            "types" : [type.name],
            "where" : {
                "value" : name,
                "property" : "name",
                "operator" : "="
            }
        }
        resp = self.session.post(url=url, data=json.dumps(body), headers=headers)
        if len(resp.json()['items']) > 0:
            return resp.json()['items'][0]['_id']
        else:
            return None

    def searchByType(self,
                     type = Type.term, pageSize=15, # type: term, category
                     properties = ["short_description","long_description","related_terms","has_a","is_of","is_a_type_of"]):
        headers = {'content-type': 'application/json'}
        url = self.url+'/ibm/iis/igc-rest/v1/search'
        body = {
            "types" : [type.name],
            "pageSize": pageSize,
            "properties": properties,
        }
        resp = self.session.post(url=url, data=json.dumps(body), headers=headers)
        if len(resp.json()['items']) > 0:
            return resp.json()['items']
        else:
            return None

    def getIdFromResponse(self, resp):
        if resp.headers.get('Location') == None: return None
        loc = resp.headers['Location']
        return loc[loc.rfind('assets/')+7::]

    def createCategory(self, name, description = '', parentCategory = None):
        headers = {'content-type': 'application/json'}
        url = self.url+'/ibm/iis/igc-rest/v1/assets/'
        body = {
            "_type" : "category",
            "name" : name,
            "short_description" : description,
            "parent_category": parentCategory
        }
        resp = self.session.post(url=url, data=json.dumps(body), headers=headers)

        if resp.status_code == 200:
            return self.getIdFromResponse(resp), resp
        else: # 400
            return self.searchForId(name, self.Type.category), resp
    
    def createTerm(self, name, short_description = '', long_description = '', parentCategory = None, isTypeOf = None, relatedTerms = None, status = 'CANDIDATE'):
        headers = {'content-type': 'application/json'}
        url = self.url+'/ibm/iis/igc-rest/v1/assets/'
        body = {
            "_type" : "term",
            "name" : name,
            "short_description" : short_description,
            "long_description" : long_description,
            "status": status,
            "parent_category": parentCategory
        }
        if isTypeOf is not None: body['is_a_type_of'] = isTypeOf
        if relatedTerms is not None: body['related_terms'] = relatedTerms
        resp = self.session.post(url=url, data=json.dumps(body), headers=headers)
        return self.getIdFromResponse(resp), resp
    
    def delete(self, id):
        if id is not None:
            url = self.url+'/ibm/iis/igc-rest/v1/assets/'+id
            resp = self.session.delete(url=url)
            return resp
        else:
            return None
        
def new(domain , password, username = 'isadmin', port = 9443, protocol = 'https'):
    return igc(domain , password, username, port, protocol)


igc_ = new('amelia15279-iis.fyre.ibm.com', 'Ibm2018!')


get_ipython().run_cell_magic('time', '', 'terms = igc_.searchByType(pageSize = 1000)\nprint(len(terms))')


for i, term in enumerate(terms):
    if term['related_terms']['paging']['numTotal'] > 0:
        print(i,term['_name'],'->',term['related_terms']['items'][0]['_name'])


terms[331]

