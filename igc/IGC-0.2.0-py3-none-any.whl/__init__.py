
# coding: utf-8

"""TODO.
"""
import json
import os
import pickle
from collections import defaultdict
from enum import Enum
from multiprocessing.dummy import Pool as ThreadPool

import requests
import urllib3

import ibm_db

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Type(Enum):
    """TODO."""

    category = 1
    term = 2


class Property(Enum):
    """TODO."""

    short_description = 1
    long_description = 2
    related_terms = 3
    has_a = 4
    is_of = 5
    is_a_type_of = 6


class Category(object):
    id = None
    client = None

    def __init__(self, id, client):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s" % (self.get_name())

    def __str__(self):
        return "%s" % (self.get_name())

    def get_id(self):
        return self.id

    def get_name(self):
        return self.client.categories_data[self.id][0]
    
    def get_description(self):
        return self.client.categories_data[self.id][1]

    def get_parent_category(self):
        if self.client.categories_data[self.id][2]:
            return self.client.categories[self.client.categories_data[self.id][2]]
        
    def get_sub_categories(self):
        resp = set()
        for i, cat in self.client.categories.items():
            if cat.get_parent_category() == self:
                resp.add(cat)
        return resp
        
    def get_full_name(self):
        resp = self.get_name()
        parent = self.get_parent_category()
        while parent:
            resp += " / "+parent.get_name()
            parent = parent.get_parent_category()
        return resp

    def get_full_path(self):
        resp = [self]
        parent = self.get_parent_category()
        while parent:
            resp.append(parent)
            parent = parent.get_parent_category()
        return resp


class Term(object):
    id = None
    client = None

    def __init__(self, id, client):
        self.id = id
        self.client = client

    def __repr__(self):
        return "%s" % (self.get_name())
        return "__Term__\nID: %s\nName: %s\nDescription: %s\nCategory: %s" % (
            self.get_id(), self.get_name(), self.get_description(),
            self.get_category())

    def __str__(self):
        return "%s" % (self.get_name())

    def get_id(self):
        return self.id

    def get_name(self):
        return self.client.terms_data[self.id][0]

    def get_description(self):
        if self.client.terms_data[self.id][2]:
            return self.client.terms_data[self.id][2]
        return self.client.terms_data[self.id][1]

    def get_category(self):
        if self.client.terms_data[self.id][3]:
            return self.client.categories[self.client.terms_data[self.id][3]]

    def get_related_terms(self):
        return self.client.related_terms[self.get_id()]

    def get_sub_terms(self):
        return self.client.sub_terms[self.get_id()]

    def get_has_terms(self):
        return self.client.has_terms[self.get_id()]

class Client(object):

    def get_terms(self):
        return self.terms

    def get_term(self, id):
        return self.terms[id]

    def get_root_terms(self):
        resp = set()
        for id, term in self.terms.items():
            if self.sub_terms_inv.get(id) == None:
                if self.sub_terms.get(id) is not None:
                    resp.add(term)
        return resp
    
    def get_category(self, id):
        return self.categories[id]

    def get_root_categories(self):
        resp = set()
        for id, cat in self.categories.items():
            if cat.get_parent_category() == None:
                resp.add(cat)
        return resp

    terms_file = 'terms.p'

    def save(self):
        pickle.dump(self.terms_data, open(self.terms_file, "wb"))
        pickle.dump(self.categories_data, open(self.terms_file+"1", "wb"))
        pickle.dump(self.sub_terms, open(self.terms_file+"2", "wb"))
        pickle.dump(self.sub_terms_inv, open(self.terms_file+"3", "wb"))

    def load(self):
        self.categories_data = pickle.load(open(self.terms_file+"1", "rb"))
        for id in self.categories_data: self.categories[id] = Category(id, self)
        self.terms_data = pickle.load(open(self.terms_file, "rb"))
        for id in self.terms_data: self.terms[id] = Term(id, self)
        self.sub_terms = pickle.load(open(self.terms_file+"2", "rb"))
        self.sub_terms_inv = pickle.load(open(self.terms_file+"3", "rb"))

    def get_category_hierarchy(self, cats = None):
        if not cats: cats = self.get_root_categories()
        resp = []
        for cat in cats:
            element = { 'id': cat.get_id(), 'name': cat.get_name() }
            if cat.get_sub_categories():
                element['subCategories'] = self.get_category_hierarchy(cat.get_sub_categories())
            resp.append( element )
        return resp

class XMETAClient(Client):
    """XMETA Client Wrapper.

    TODO
    """

    def __init__(self,
                 domain,
                 password,
                 database='XMETA',
                 port=50000,
                 protocol='TCPIP',
                 user_id='db2inst1',
                 fetch=True):
        self.conn = ibm_db.connect(
            "DATABASE=" + database + ";HOSTNAME=" + domain + ";PORT=" +
            str(port) + ";PROTOCOL=" + protocol + ";UID=" + user_id + ";PWD=" +
            password + ";", "", "")
        self.terms_data = {}
        self.terms = {}
        self.related_terms = defaultdict(set)
        self.sub_terms = defaultdict(set)
        self.has_terms_inv = defaultdict(set)
        self.has_terms = defaultdict(set)
        self.sub_terms_inv = defaultdict(set)
        self.main_objects = {}
        self.assigned_objects = defaultdict(set)
        self.categories_data = {}
        self.categories = {}

        if fetch: self.fetch()

    def fetch(self,
              terms=True,
              sub_terms=True,
              related_terms=True,
              has_terms=True,
              fetch_categories=True,
              main_objects=False,
              assigned_assets=False):
        if terms: self.fetch_terms()
        if sub_terms: self.fetch_sub_terms()
        if has_terms: self.fetch_has_terms()
        if related_terms: self.fetch_related_terms()
        if fetch_categories: self.fetch_categories()
        if main_objects: self.fetch_main_objects()
        if assigned_assets: self.fetch_assigned_assets()

    def fetch_terms(self):
        stmt = ibm_db.exec_immediate(self.conn, """
        SELECT
         XMETA_REPOS_OBJECT_ID_XMETA,
         NAME_XMETA,
         SHORTDESCRIPTION_XMETA,
         LONGDESCRIPTION_XMETA,
         CONTAINER_RID
        FROM
         XMETA.GLOSSARYEXTENSIONS_BUSINESSTERM
        """)
        tuple = ibm_db.fetch_tuple(stmt)
        while tuple != False:
            self.terms_data[tuple[0]] = tuple[1:]
            self.terms[tuple[0]] = Term(tuple[0], self)
            tuple = ibm_db.fetch_tuple(stmt)

    def fetch_related_terms(self):
        stmt = ibm_db.exec_immediate(self.conn, """
        SELECT
         *
        FROM
         XMETA.GLOSSARYEXTENSIONS_BUSINESSTERM_HASRELATED_BUSINESSTERM_RELATESTO_BUSINESSTERM
         """)
        tuple = ibm_db.fetch_tuple(stmt)
        while tuple != False:
            self.related_terms[tuple[0]].add(self.terms[tuple[1]])
            tuple = ibm_db.fetch_tuple(stmt)

    def fetch_sub_terms(self):
        stmt = ibm_db.exec_immediate(self.conn, """
        SELECT
         *
        FROM
         IGVIEWS.IGTERMHASSUBTERM
         """)
        tuple = ibm_db.fetch_tuple(stmt)
        while tuple != False:
            self.sub_terms[tuple[0]].add(str(self.terms[tuple[1]]))
            self.sub_terms_inv[tuple[1]].add(str(self.terms[tuple[0]]))
            tuple = ibm_db.fetch_tuple(stmt)

    def fetch_has_terms(self):
        stmt = ibm_db.exec_immediate(self.conn, """
        SELECT
        *
        FROM
         IGVIEWS.IGTERMHASTERM
         """)
        tuple = ibm_db.fetch_tuple(stmt)
        while tuple != False:
            self.has_terms[tuple[0]].add(self.terms[tuple[1]])
            self.has_terms_inv[tuple[1]].add(self.terms[tuple[0]])
            tuple = ibm_db.fetch_tuple(stmt)

    def fetch_main_objects(self):
        stmt = ibm_db.exec_immediate(self.conn, """
        SELECT
         XMETA_REPOS_OBJECT_ID_XMETA,
         NAME_XMETA,
         SHORTDESCRIPTION_XMETA,
         LONGDESCRIPTION_XMETA,
         CONTAINER_RID
        FROM
         XMETA.VWASCLMODEL_MAINOBJECT
         """)
        tuple = ibm_db.fetch_tuple(stmt)
        while tuple != False:
            self.main_objects[tuple[0]] = tuple[1:]
            tuple = ibm_db.fetch_tuple(stmt)

    def fetch_assigned_assets(self):
        stmt = ibm_db.exec_immediate(self.conn, """
        SELECT
         *
        FROM
         IGVIEWS.IGASSIGNEDOBJECTSOFATERM
        """)
        tuple = ibm_db.fetch_tuple(stmt)
        while tuple != False:
            self.assigned_objects[tuple[1]].add(tuple[0])
            tuple = ibm_db.fetch_tuple(stmt)

    def fetch_categories(self):
        stmt = ibm_db.exec_immediate(self.conn, """
        SELECT
         XMETA_REPOS_OBJECT_ID_XMETA,
         NAME_XMETA,
         SHORTDESCRIPTION_XMETA,
         CONTAINER_RID,
         GLOSSARYTYPE_XMETA,
         XMETA_OPTIMISTIC_LOCK_ID_XMETA
        FROM
         XMETA.GlossaryExtensions_BusinessCategory
        """)
        tuple = ibm_db.fetch_tuple(stmt)
        while tuple != False:
            self.categories_data[tuple[0]] = tuple[1:]
            self.categories[tuple[0]] = Category(tuple[0], self)
            tuple = ibm_db.fetch_tuple(stmt)
            
    def insert_categories(self):
        for id, c in self.categories_data.items():     
            stmt = ibm_db.prepare(self.conn, """
            INSERT INTO XMETA.GlossaryExtensions_BusinessCategory
             (XMETA_REPOS_OBJECT_ID_XMETA,
             NAME_XMETA,
             SHORTDESCRIPTION_XMETA,
             CONTAINER_RID,
             GLOSSARYTYPE_XMETA,
             XMETA_OPTIMISTIC_LOCK_ID_XMETA)
            VALUES (?,?,?,?,?,?)""")
            ibm_db.bind_param(stmt, 1, id)
            ibm_db.bind_param(stmt, 2, c[0])
            ibm_db.bind_param(stmt, 3, c[1])
            ibm_db.bind_param(stmt, 4, c[2])
            ibm_db.bind_param(stmt, 5, c[3])
            ibm_db.bind_param(stmt, 6, c[4])
            ibm_db.execute(stmt)

    def delete_categories(self):
        stmt = ibm_db.exec_immediate(self.conn, """
         DELETE FROM XMETA.GlossaryExtensions_BusinessCategory
        """)
            
            
class IGCRESTClient(Client):
    """IGC Rest Client Wrapper.

    TODO
    """

    session = requests.Session()
    session.verify = False
    assetCache = dict()

    pool = ThreadPool(8)
    
    def __init__(self,
                 domain,
                 password,
                 username='isadmin',
                 port=9443,
                 protocol='https',
                 load_cached_terms=False):
        
        if port == 443:
            self.url = protocol + '://' + domain
        else:
            self.url = protocol + '://' + domain + ':' + str(port)
        self.session.auth = (username, password)
        
        self.terms_data = {}
        self.terms = {}
        self.related_terms = defaultdict(set)
        self.sub_terms = defaultdict(set)
        self.has_terms_inv = defaultdict(set)
        self.has_terms = defaultdict(set)
        self.sub_terms_inv = defaultdict(set)
        self.main_objects = {}
        self.assigned_objects = defaultdict(set)
        self.categories_data = {}
        self.categories = {}
        
        if load_cached_terms: self.load_terms()

    def logout(self):
        self.session.get(self.url + "/ibm/iis/igc-rest/v1/logout/")

    def get_asset_(self, id, property='', use_cache=True):
        if self.assetCache.get(id + property) is None or use_cache is False:
            url = self.url + '/ibm/iis/igc-rest/v1/assets/' + id + '/' +                property
            resp = self.session.get(url=url)
            self.assetCache[id + property] = resp.json()
        return self.assetCache[id + property]

    def search_for_id_(self, name, type=Type.term):
        headers = {'content-type': 'application/json'}
        url = self.url + '/ibm/iis/igc-rest/v1/search'
        body = {
            "types": [type.name],
            "where": {
                "value": name,
                "property": "name",
                "operator": "="
            }
        }
        resp = self.session.post(
            url=url, data=json.dumps(body), headers=headers)
        if len(resp.json()['items']) > 0:
            return resp.json()['items'][0]['_id']
        else:
            return None

    def get_id_from_response(self, resp):
        if resp.headers.get('Location') is None:
            return None
        loc = resp.headers['Location']
        return loc[loc.rfind('assets/') + 7::]

    def create_category(self, name, description='', parent_category=None):
        headers = {'content-type': 'application/json'}
        url = self.url + '/ibm/iis/igc-rest/v1/assets/'
        body = {
            "_type": "category",
            "name": name,
            "short_description": description,
            "parent_category": parent_category
        }
        resp = self.session.post(
            url=url, data=json.dumps(body), headers=headers)

        if resp.status_code == 200:
            return self.get_id_from_response(resp), resp
        else:  # 400
            return self.search_for_id(name, Type.category), resp

    def create_term(self,
                    name,
                    short_description='',
                    long_description='',
                    parent_category=None,
                    is_type_of=None,
                    related_terms=None,
                    status='CANDIDATE'):
        headers = {'content-type': 'application/json'}
        url = self.url + '/ibm/iis/igc-rest/v1/assets/'
        body = {
            "_type": "term",
            "name": name,
            "short_description": short_description,
            "long_description": long_description,
            "status": status,
            "parent_category": parent_category
        }
        if is_type_of is not None:
            body['is_a_type_of'] = is_type_of
        if related_terms is not None:
            body['related_terms'] = related_terms
        resp = self.session.post(
            url=url, data=json.dumps(body), headers=headers)
        return self.get_id_from_response(resp), resp

    def delete(self, id):
        if id is not None:
            url = self.url + '/ibm/iis/igc-rest/v1/assets/' + id
            resp = self.session.delete(url=url)
            return resp
        return None

    def get_assets_by_type(self,
                           type=Type.term,
                           properties=[],
                           page_size=10,
                           page=0):
        headers = {'content-type': 'application/json'}
        url = self.url + '/ibm/iis/igc-rest/v1/search'
        body = {
            "types": [type.name],
            "pageSize": page_size,
            "properties": [i.name for i in properties],
            "begin": page * page_size
        }
        resp = self.session.post(
            url=url, data=json.dumps(body), headers=headers)
        if len(resp.json()['items']) > 0:
            return resp.json()['items']
        else:
            return None

    def get_assets_by_type_count(self, type=Type.term):
        headers = {'content-type': 'application/json'}
        url = self.url + '/ibm/iis/igc-rest/v1/search'
        body = {"types": [type.name], "pageSize": 1, "properties": []}
        resp = self.session.post(
            url=url, data=json.dumps(body), headers=headers)
        return resp.json()['paging']['numTotal']

    def parallel_request(self, page, page_size=100):
        assets = self.get_assets_by_type(
            Type.term,
            properties=[
                Property.related_terms,
                Property.short_description,
                Property.long_description
            ],
            page_size=page_size,
            page=page)
        return assets

    def fetch_all_terms(self):
        numTotal = self.get_assets_by_type_count()
        pages = round(numTotal / 100 + 0.5)
        for i in self.pool.imap_unordered(self.parallel_request, range(pages)):
            for t in i:
                # term itself
                categories = t['_context']
                self.terms_data[t['_id']] = (t['_name'],t['short_description'],t['long_description'],categories[len(categories)-1]['_id'])
                self.terms[t['_id']] = Term(t['_id'], self)
                
                # related terms
                for rt in t['related_terms']['items']:
                    if self.terms.get(rt['_id']) == None:
                        # add placeholder
                        self.terms[rt['_id']] = Term(rt['_id'], self)
                    self.related_terms[t['_id']].add(self.terms[rt['_id']])
                
                # category
                for i, category in enumerate(categories):
                    if self.categories.get(category['_id']) == None:
                        parent_category = None
                        if i > 0: parent_category = categories[i-1]['_id']
                        self.categories_data[category['_id']] = (category['_name'],'',parent_category)
                        self.categories[category['_id']] = Category(category['_id'], self)

    def get_all_term_mappings_(self):
        res = []
        for id in self.terms:
            if self.terms[id][Property.related_terms.name]['paging']['numTotal'] > 0:
                for rterm in [
                        i['_name']
                        for i in self.terms[id]['related_terms']['items']
                ]:
                    res.append((self.get_term(id)['_name'], rterm))
        return res


def new(domain,
        password,
        username='isadmin',
        port=9443,
        protocol='https',
        load_cached_terms=False):
    return IGCRESTClient(domain, password, username, port, protocol,
                     load_cached_terms)

