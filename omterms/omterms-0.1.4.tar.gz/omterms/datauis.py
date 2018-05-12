# -*- coding: utf-8 -*-
"""OpenMaker textaul data holders and interfaces.

Author: Bulent Ozel
e-mail: bulent.ozel@gmail.com

The module contains a set of tools used to hold and process text corpuses and collections.

"""

from nltk import FreqDist
import json, copy
import pandas as pd

class WikiArticles(object):
    """The object contains a set of tools to process the set of 
        documents collected and cleaned by the wiki crawler.

    Attributes:
        collection_json (:obj:`str`): This is a filename to the scraped data.
            Each JSON document is expected to have following fields:
            - theme: Topic identifier, ex: Sustainability
            - theme.id: A unique category identifier
            - document.id: A unique document id
            - title: Title of the document
            - url: Full URL of the document
            - depth: The link distance from the seed docuement. The seed documents depth is 0.
            - text: The string data scraped from the page without tags. Pancuations are not 
                required but terms are expected to be delineated by white space. 
        collection (:obj:`list` of :obj:`dict`): Loaded json file into native list of dictionaries.
    
    """
    
    def __init__(self, collection):
        """The class constructor.

        Args:
            collection (:obj:`str`): A filename to a previously scraped data.

        """
        self.collection_json = collection
        self.load_corpus()
        
        
    def load_corpus(self, collection = None):
        """The method loads imports json file into a native collection.
          
        Args:
            collection (:obj:`str`): A filename to a previously scraped data.
                
        Returns:
            (:obj:`bool`): True.
            
        """
            
        if collection:
            self.collection_json = collection
        with open(self.collection_json, "r") as f:
            _text = f.read()
        self.collection = json.loads(_text)
        print('Number of documents in the corpus: {}\n'.format(len(self.collection)))
        return True
    
    
    def get_document_fields(self):
        """The method lists the fields of each json field of its collection.
          
        Args:
            None  
            
        Returns:
            (:obj:`dict_keys`): List of keys.
            None: When the collection is empty.
            
        """
        msg = '{} must have been a non-empty list of dict objects'.format(self.collection)
        assert isinstance(self.collection, list), msg
        if not len(self.collection): return
        return self.collection[0].keys()
    
    
    def list_themes(self):
        """The method lists the summary of themes/topics in the collection.
          
        Args:
            None  
            
        Returns:
            (:obj:`list` of :obj:`dict`): List of dictionry where keys are
                - name: theme's textual descriptor
                - id: theme's unique id
                - count: number of articles under the theme.   
        
        """
        themes = dict()
        count = 0
        for article in self.collection:
            theme_id = article['theme.id']
            if theme_id not in themes.keys():
                themes[theme_id] = (article['theme'], 0)
            else:
                t,c = themes[theme_id]
                c += 1
                themes[theme_id] = (t, c)
        themes = [{'id':k, 'name':v[0], 'num_of_articles':v[1]} for k,v in themes.items()]
        return themes

    
    def get_theme_title(self, theme_id):
        """The method returns topic name.
          
        Args:
            theme_id (:obj:`int`): The unique theme id. 
            
        Returns:
            ( :obj:`str`): Topic name.  
        
        """
        title = None
        for article in self.collection:
            if article['theme.id'] == theme_id:
                title = article['theme']
                break
        return title

    def get_theme_id(self, theme_name):
        """The method returns topic id of the first match theme name.
          
        Args:
            theme_name (:obj:`str`): The theme or topic name. 
            
        Returns:
            ( :obj:`int`): A unique theme identifier.  
        
        """
        theme_id = None
        for article in self.collection:
            if article['theme'] == theme_name:
                theme_id = article['theme.id']
                break
        return int(theme_id)

    
    def display_documents_list(self, tid=None, stdout = True):
        """List the articles meta data and crawling information on them.
        
        Args:
            tid (:obj:`int`, optional): Used if documents info under a specific theme is desired 
                otherwise a summary of whole set is returned or displayed (default None).
            stdout (:obj:`bool`, optional): Whether the info is to be displayed/printed
                to standard io (default True).
                
        Returns:
            ( :obj:`list`): A summary list of documents in the collection. 
            

        """
        if stdout: print('document.id :: theme.id :: theme :: depth :: url')
        articles = copy.deepcopy(self.collection)
        for a in articles:
            if 'text' in a:
                del a['text']
        if tid:
            articles = [a for a in articles if a['theme.id'] == tid]   
        articles = sorted(articles, key=lambda x: (x['theme.id'], x['depth']))
        if not stdout: return articles
        for a in articles:
            print(a['document.id'],a['theme.id'],a['theme'],a['depth'],a['url'])
        return articles
    

    def prune(self, themes_to_keep = [], docs_to_drop = [], istodrop = lambda x: False):
        """The method is used to filter out documents from the set.
            The order of prunning is as follows:
            - when a none empty list is provide all the documents not belonging themes to be kept
                are prunned entirely. Note that when initial list is empty it doesn't have an effect.
            - of remaing documents those appear in docs_to_drop are prunned
            - of the remaing docs those produce a True at a call on the predicate function are dropped.
            
            The function can be repeatedly called until a desired level of prunning is achieved.
        
        Args:
            themes_to_keep (:obj:`list` of :obj:`int`, optional): The list of theme ids to be kept (default Empty).
            docs_to_drop (:obj:`list`, optional): The list of doc ids to be dropt (default Empty). 
            f (x :obj:`dict_item` -> :obj:`bool`, optional): A predicate function (default lambda x:False)
            
        Returns:
            (:obj:`bool`): True. 

        """
        if themes_to_keep:
            themes = list(map(lambda x: int(x), themes_to_keep))
            self.collection = [a for a in self.collection if int(a['theme.id']) in themes]
        self.collection = [a for a in self.collection if a['document.id'] not in docs_to_drop]
        self.collection = [a for a in self.collection if not istodrop(a)]
        return True


    def collate(self, by_theme_id = None, by_doc_ids = [], marker = "\n"):
        """The method collects the desired set of documents concatenates them creating a unified document.
            The order of merge is as follows:
            - When neither list of theme nor doc ids is provided, it collates entire text.
            - If a theme is given then all the documents under that theme are to be joined first.
            - When a list of docs is given, only those in the list are kept.
            Note that if both theme id and doc ids provided, precedence is on themes.
        
        Args:
            by_theme_id (:obj:`int`, optional): The theme id of the docs to be collated.
            by_doc_ids (:obj:`list` of :obj:`int`, optional): The list of doc ids to be collated (default Empty). 
            marker (:obj:`str`, optional): A delimiter (default newline)
            
        Returns:
            (:obj:`str`): The collated text. 
        
        """
        docs =  self.collection
        if by_theme_id:
            docs = [d for d in docs if d['theme.id'] == by_theme_id]
        if by_doc_ids:
            docs = [d for d in docs if d['document.id'] in by_doc_ids]
        texts = [d['text'] for d in docs]
        text = marker.join(texts)
        return text
 
class Corpus(object):
    """A generic class to be used for foreground or background corpuses.

    Attributes:
        tf_dist: (:obj:`nltk.FreqDist`): An NLTK container for tokenized and cleaned
            terms in the corpus.
        stemmer (x :obj:`str` -> y: :obj:`str`): A stemmer function.
        stems (:obj:`dict`): A dictionary of terms and their stems
        labels (:obj:`dict`): Term level labels.
        scores (:obj:`dict`): A dictionary of terms and their corpus sepcificity scores
            as of a reference corpus
        ref (:obj:`dict`): A dictionary of terms that holds normalized occurance frequency of
            the term at a reference corpus.
        sepficifs (:obj:`set`): A set of terms appointed/associated with the corpus externally.        
        To be implemented:
            texts_raw (:obj:`json`): A JSON collection of raw texts of the corpus.
        
            texts_clean (:obj:`json`): A JSON collection of cleaned/processed
            texts of the corpus.
        
            tf_idf (:obj:`json`): Tf-Idf analyses of the corpus (to be implemented).
        
    """

    def __init__(self, tf_dist, stemmer = None):
        """The class constructor.

        Args:
            tf_dist (:obj:`nltk.FreqDist`): An NLTK container for tokenized and cleaned
            terms in the corpus.
            stemmer (x :obj:`str` -> y: :obj:`str`): A stemmer function (default None)

        """
        self.tf_dist = tf_dist
        self.stemmer = stemmer if stemmer else lambda x:x
        self.stems = dict()
        self.labels = dict()
        self.scores = dict()
        self.ref = dict()
        self.specifics = set()
        

    def get_top_frequents(self, top=42):
        """The method identifies and returns top frequent terms.
        
        Args:
            top (int): Size of the short list (default 42).
            
        Returns:
            (:obj:`list` of :obj:`tuple` of :obj:`str` and :obj:`int`): Returns the frequency dist
                for top terms as list of tuples of term and frequency pairs.

        """
        return self.tf_dist.most_common(top)
    
    def get_least_frequents(self, bottom=42):
        """The method identifies and returns least frequent terms.
        
        Args:
            bottom (int): Size of the short list (default 42).
            
        Returns:
            (:obj:`list` of :obj:`tuple` of :obj:`str` and :obj:`int`): Returns the frequency dist
                for the least frequent terms as list of tuples of term and frequency pairs.

        """
        _n = self.get_count_uniques()
        slice_from = _n - bottom if _n > bottom else 0
        return self.tf_dist.most_common(_n)[slice_from:]
    
    def get_count_uniques(self):
        """The method identifies and returns top frequent terms.
            
        Returns:
            (:obj:`int`): Returns an integer.

        """
        return self.tf_dist.B()

    def get_size(self):
        """The returns the size of the corpus in terms of number of terms it has.
            
        Returns:
            (:obj:`int`): Returns an integer. It is summation of raw frequency counts.

        """
        return self.tf_dist.N()
    
    def union(self, other,
              as_corpus = False,
              stats = False):
        """The method identifies and returns the union of two corpora.
        
        Args:
            other (:obj:`Corpus`): An instance of this Class object.
            as_corpus (bool): When True it returns a new Corpus (default False).
            stats (bool): When True and as_corpus is false returns the frequency 
                count of the union.
            
        Returns:
            (:obj:`list` of :obj:`str`): If as_corpus is False and stats is False 
                it returns the list of union of terms in both cases.
            (:obj:`list` of :obj:`tuple` of :obj:`str` and :obj:`int`): Returns the frequency dist
                for the union terms, ff as_corpus is False and stats is True. 
            (:obj:`Corpus`): In all other cases it returns a nrew Corpus class for the intersection.
                Frequencies are the minimum of the two occurances.
        
        Examples:
            >>> Corpus(FreqDist('abbbc')).union(Corpus(FreqDist('bccd')), stats = True)
            [('a', 1), ('b', 3), ('c', 2), ('d', 1)]

        """
        Union = self.tf_dist | other.tf_dist
        if not as_corpus and not stats: return list(Union.keys())
        if not as_corpus and stats: return list(Union.items())
        return Corpus(Union)
    
    def intersection(self, other,
                     as_corpus = False,
                     stats = False):
        """The method identifies and returns the intersection of two corpora.
        
        Args:
            other (:obj:`Corpus`): An instance of this Class object.
            as_corpus (bool): When True it returns a new Corpus (default False).
            stats (bool): When True and as_corpus is false returns the frequency 
                count of the intersections.
            
        Returns:
            (:obj:`list` of :obj:`str`): If as_corpus is False and stats is False 
                it returns the list of joint terms.
            (:obj:`list` of :obj:`tuple` of :obj:`str` and :obj:`int`): Returns the frequency dist
                for the joint terms, if as_corpus is False and stats is True. 
            (:obj:`Corpus`): In all other cases it returns a nrew Corpus class for the intersection.
                Frequencies are the minimum of the two occurances.

        """
        Common = self.tf_dist & other.tf_dist
        if not as_corpus and not stats: return list(Common.keys())
        if not as_corpus and stats: return list(Common.items())
        return Corpus(Common)
    
    def difference(self, other,
              as_corpus = False,
              stats = False):
        """The method identifies and returns the difference of the self from the other.
        
        Note:
            Implementation needs style and refactoring.
            
        Args:
            other (:obj:`Corpus`): An instance of this Corpus Class object.
            as_corpus (bool): When True it returns a new Corpus (default False).
            stats (bool): When True and as_corpus is false returns the frequency 
                count of the difference set.
            
        Returns:
            (:obj:`dict`): A dictionary of terms and their frequency counts.
            
        """
        joint = set(self.intersection(other))
        difference = set(self.tf_dist.keys()).difference(joint)
        return {k:v for k, v in self.tf_dist.items() if k in difference}
    
    def plot(self, top, cumulative = False):
        """Plotting.
        
        Note:
            
        Returns:
            (:obj:`bool`): True
            
        """
        self.tf_dist.plot(top, cumulative = cumulative)
        return True
    
    def tabulate(self, top):
        """Tabulating.
        
        Note:
            Works better when used to see few top terms.
            
        Returns:
            (:obj:`bool`): True
            
        """
        self.tf_dist.tabulate(top) 
        return True
    
    def list_terms(self):
        """It returns the list terms in the corpus
        
        Note:
            Implementation needs refactoring.
            
        Returns:
            (:obj:`list`): An alphabetically sorted list.
            
        """
        return list(sorted(self.tf_dist.keys()))

    
    def set_stemmer(self, stemmer):
        """The appointing a new stemmer function to the corpus.
        
        Args:
            stemmer (x :obj:`str` -> y: :obj:`str`): A stemmer function (default None)
            
        Returns:
            (:obj:`bool`): True
            
        """
        
        self.stemmer = stemmer
        return True
        
    
    def compute_stems(self):
        """The function returns the a dictionary of terms and their corresponding stems.
        
        Args:
            stemmer (x :obj:`str` -> y: :obj:`str`): A stemmer function (default None)
            
        Returns:
            (:obj:`bool`): True
            
        """
        self.stems = {k: self.stemmer(k) for k in self.list_terms()}
        return True
        # Follwing bit is used to test NLTK stemmer
        for k in self.list_terms():
            print(k)
            self.stems[k] = self.stemmer(k)
        
    
    
    def get_stems(self):
        """The function returns the a dictionary of terms and their corresponding stems.
        
        Args:
            
        Returns:
            (:obj:`dict`): A dictionary of {term:stem of the term}.
            
        """
        if self.stems: return self.stems
        self.compute_stems()
        return self.stems
    
    def label(self, marker, labels=None):
        """The function labels yet not labeled terms according to the user defined scheme.
        
        Args:
            marker (x :obj:`str` -> y: :obj:`str`): A marker function
            
        Returns:
            (:obj:`dict`): A dictionary of {term:label of term}.
            
        """
        if not labels: labels = {t:None for t in self.list_terms()}
        for t,v in labels.items():
            if v: continue
            labels[t] = marker(t)
        self.labels = labels
        return self.labels
    
    def set_specific_set(self, terms):
        """The function sets the set of corpus specific terms.
        
        Args:
            terms (:obj:`set`): The list of corpus specific terms
            
        Returns:
            (:obj:`bool`): True.
            
        """
        self.specifics = set(terms)
        return True
    
    def to_pandas(self):
        """The function exports its data into pandas dataframe.
        
        Note:
            ToDo: The function needs parameterization, generalization and error checks.
        
        Returns:
            (:obj:`pandas.DataFrame`) The tabulated data
            
        """
        DF = pd.DataFrame({'Term':list(self.tf_dist.keys()), 'TF':list(self.tf_dist.values())})
        wTF = {w:self.tf_dist.freq(w) for w,c in self.tf_dist.items()}
        wTF = pd.DataFrame({'Term':list(wTF.keys()), 'wTF':list(wTF.values())})
        Stem = pd.DataFrame({'Term':list(self.stems.keys()), 'Stem':list(self.stems.values())})
        Score = pd.DataFrame({'Term':list(self.scores.keys()), 'Score':list(self.scores.values())})
        SType = pd.DataFrame({'Term':list(self.labels.keys()), 'SType':list(self.labels.values())})
        wTFref = pd.DataFrame({'Term':list(self.ref.keys()), 'wTFref':list(self.ref.values())})
        if not Stem.empty: DF = pd.merge(DF, Stem, on='Term', how='outer')
        if not wTF.empty: DF = pd.merge(DF, wTF, on='Term', how='outer') 
        if not SType.empty: DF = pd.merge(DF, SType, on='Term', how='outer')
        if not Score.empty: DF = pd.merge(DF, Score, on='Term', how='outer')
        if not wTFref.empty: DF = pd.merge(DF, wTFref, on='Term', how='outer')
        order = ['wTF','TF'] if  'wTF' in DF.columns else ['TF']
        if  'Score' in DF.columns: order = ['Score'] + order
        DF = DF.sort_values(by=order, ascending = False)
        return DF
        
        # Redundant and is never run, it is from the initial version
        wTFd = {w:self.tf_dist.freq(w) for w,c in self.tf_dist.items()}
        wTF = pd.Series(wTFd, name= 'wTF')
        wTF.index.name = 'Term'
        
        TF = pd.Series(dict(self.tf_dist.items()), name='TF')
        TF.index.name = 'Term'
        
        Stem = pd.Series(self.stems, name='Stem')
        Stem.index.name = 'Term'
        
        Score = pd.Series(self.scores, name='Score')
        Score.index.name = 'Term'
        
        SType = pd.Series(self.labels, name='sType')
        SType.index.name = 'Term'
        
        wTFref = pd.Series(self.ref, name='wTFref')
        wTFref.index.name = 'Term'
        
        if not Stem.empty:
            DF = Stem.to_frame()
            DF = DF.merge(TF.to_frame(), left_index=True, right_index=True)
        else:
            DF = TF.to_frame()
            
        if not wTF.empty:
            DF = DF.merge(wTF.to_frame(), left_index=True, right_index=True)
            
        if not Score.empty:
            DF = DF.merge(Score.to_frame(), left_index=True, right_index=True)
            
        if not SType.empty:
            DF = DF.merge(SType.to_frame(), left_index=True, right_index=True)
            
        if not wTFref.empty:
            DF = DF.merge(wTFref.to_frame(), left_index=True, right_index=True)
        return DF
  