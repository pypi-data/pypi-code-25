# -*- coding: utf-8 -*-
"""OpenMaker text cleaner.

Author: Bulent Ozel
e-mail: bulent.ozel@gmail.com

The module contains a set of tools to clean textual data.

"""

from nltk import FreqDist
import re, copy
import pprint as pp


from omterms import tokenizer

class TextCleaner(object):
    """An object that contains a set of tools to clean and preprocess textual data.

    Note:
        The object uses nltk.FreqDist object
        For stem checks during pruninng it needs an external stemmer.
    
    Attributes:
        exceptions (:obj:`list` of :obj:`str`): List of excepted terms.
        stopwords (:obj:`list` of :obj:`str`): List of stopwords.
        stemf: A stemmer funtion.
    
    """
    
    def __init__(self,
                 stopwords = [],
                 exceptions = [],
                 fstemmer = lambda x:x, 
                 stemcheck = False):
        """The class constructor.

        Args:
            stopwords (:obj:`list` of :obj:`str`, optional): list of stopwords (default None).
            exceptions (:obj:`set` of :obj:`str`, optional): list of excepted terms (default None).
            fstemmer (x :obj:`str` -> y: :obj:`str`, optional): A stemmer function (default f(x) = x)
            stemcheck (:obj:`bool`): A flag to determine whether stems of exceptions should also be considered
                (default False)
            
        """
        try:
            from nltk import FreqDist
        except:
            raise  ImportError("It wasn't possible to import 'nltk.FreqDist.")
        self.stopwords = stopwords
        self.stemf =  fstemmer
        self.exceptions = self.make_exceptions(exceptions, stemcheck)
     
    
    def load_stopwords(self, spointer):
        """The method reloads a new stopwords list.

        Note:
            Internal stopword is overwritten.
            
        Args:
            spointer (:obj:`list` of :obj:`str`or :obj:`str`): Either file path string or
                a list of stopwords.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            FileNotFoundError: Raised if a given file is not accessable.

        """
        if isinstance(spointer, (list, set)):
            self.stopwords = set(spointer)
            return True
        
        with open(spointer, "r") as f:
            self.stopwords = set(f.read().strip().split("\n"))    
        return True
    
    def extend_stopwords(self, spointer):
        """The method extends a new stopwords list.
            
        Args:
            spointer (:obj:`list` of :obj:`str`, :obj:`str`): Either file path string or
                a list of stopwords.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            FileNotFoundError: Raised if a given file is not accessable.

        """
        if isinstance(spointer, (list, set)):
            sws = set(spointer)
        else:
            with open(spointer, "r") as f:
                newwords = set(f.read().strip().split("\n"))
                sws = set(newwords)
        if not sws: return False
        self.stopwords = self.stopwords.union(sws) if self.stopwords else sws
        return True
    
    @staticmethod
    def freq_dist(words):
        """The static method computes frequency distribution of a word list.
            
        Args:
            words (:obj:`list` of :obj:`str`, :obj:`str`): list of words.

        Returns:
            (:obj:`nltk.FreqDist`): Returns frequency dist.

        """
        return FreqDist([w.lower() for w in words])
    
    def clean(self, words, display_top = 10, logging = True, exceptions = []):
        """Removes panctuations and stopwords from a corpus.
            
        Args:
            words (:obj:`list` of :obj:`str`): The input corpus as list of words.
            display_top (:obj:`int`, optional): Logging size (default 10).
            logging (:obj:`bool`): Optional. When true stdout logging is done (default True).
            exceptions (:obj:`list` of :obj:`str`, optional): The list terms that will not 
                be pruned (default None).

        Returns:
            (:obj:`nltk.FreqDist`): Returns the trimmed corpus as the NLTK obj.

        """
        def report(headline, fd):
            """Local method for logging the updates.
            
            Args:
                headline (:obj:`str`): The state description

            Returns:
                logging (:obj:`bool`): True.
            """
            print(headline)
            print('Total term counts: {}'.format(sum(fd.values())))
            pp.pprint(fd.most_common(display_top))
            return True
        
        FD = TextCleaner.freq_dist(words)
        headline = "Initial state:"
        if logging: report(headline, FD)
        
        FD = self.remove_panctuation(FD, exceptions = exceptions)
        headline = "Removing panctuation only terms..."
        if logging: report(headline, FD)

        FD = self.remove_stopwords(FD, exceptions = exceptions)
        headline = "Removing stopwords..."
        if logging: report(headline, FD)
        return FD
        
    
    def remove_panctuation(self, freq_dist, exceptions = []):
        """The static method removes punctuation only terms.
            
        Args:
            freq_dist (:obj:`nltk.FreqDist`): list of words and more.
            exceptions (:obj:`list` of :obj:`str`, optional): The exception list.

        Returns:
            (:obj:`nltk.FreqDist`): Returns frequency dist.

        """
        for punctuation in tokenizer.CHARACTERS_TO_SPLIT:
            if punctuation in exceptions: continue
            dp = punctuation * 2
            tp = dp + punctuation
            if punctuation in freq_dist.keys():
                del freq_dist[punctuation]
            if dp in freq_dist.keys():
                del freq_dist[dp]
            if tp in freq_dist.keys():
                del freq_dist[tp]
        return freq_dist
    
    def remove_stopwords(self, freq_dist, exceptions = []):
        """The static method removes stopwords.
            
        Args:
            freq_dist (:obj:`nltk.FreqDist`): list of words and more.
            exceptions (:obj:`list` of :obj:`str`, optional): The exception list.

        Returns:
            (:obj:`nltk.FreqDist`): Returns frequency dist.

        """
        for term in self.stopwords:
            if self.isexception(term, exceptions): continue
            if term in freq_dist.keys():
                del freq_dist[term]
        return freq_dist
    
    def remove_numerals(self, freq_dist, remove_any = False, exceptions = []):
        """The method removes terms with numeral literals.
            
        Note:
            When remove_any is selected, literals such as 3D would vanish.
            
        Args:
            freq_dist (:obj:`nltk.FreqDist`): list of words and more.
            remove_any (:obj:`bool`, optional): If True mumeral and literal mixed terms are removed.
            exceptions (:obj:`list` of :obj:`str`, optional): The exception list.

        Returns:
            (:obj:`nltk.FreqDist`): Returns frequency dist.

        """
        freq_distN = copy.deepcopy(freq_dist)
        if remove_any:
            pattern_numbers = re.compile('[0-9]')
            def has_numbers(x):
                return(pattern_numbers.search(x) is not None)
            for term in freq_dist.keys():
                if self.isexception(term, exceptions, stemcheck=True): continue
                if has_numbers(term):
                    #print(term)
                    del freq_distN[term]
        else:
            pattern_letters = re.compile('[a-z]')
            def has_letters(x):
                return(pattern_letters.search(x) is not None)
            for term in freq_dist.keys():
                if self.isexception(term, exceptions, stemcheck=True): continue
                if not has_letters(term):
                    #print(term)
                    del freq_distN[term]
        return freq_distN
                
    def remove_short_terms(self, freq_dist, threshold = 1, exceptions = []):
        """The method removes terms that are below a certain length.
        
        Args:
            freq_dist (:obj:`nltk.FreqDist`): list of words and more.
            threshold (:obj:`int`, optional): The charcter length of a term (default 1).
            exceptions (:obj:`list` of :obj:`str`, optional): The exception list.

        Returns:
            (:obj:`nltk.FreqDist`): Returns frequency dist.

        """
        freq_distN = copy.deepcopy(freq_dist)
        for term in freq_dist.keys():
            if self.isexception(term, exceptions): continue
            if len(term) <= threshold:
                del freq_distN[term]
        return freq_distN

    def remove_rare_terms(self, freq_dist, below = 3, exceptions = []):
        """The method removes terms that have rare occurances.
        
        Note:
            Such removal may help reduce errenous and random terms.
            
        Args:
            freq_dist (:obj:`nltk.FreqDist`): list of words and more.
            below (:obj:`int`, optional): The minumum allowed frequency count (default 3).
            exceptions (:obj:`list` of :obj:`str`, optional): The exception list.

        Returns:
            (:obj:`nltk.FreqDist`): Returns frequency dist.

        """
        freq_distN = copy.deepcopy(freq_dist)
        for term in freq_dist.keys():
            if term in exceptions: continue
            if freq_dist[term] < below:
                del freq_distN[term]
        return freq_distN
    
    
    @staticmethod
    def make_exceptions(exceptions, stemf = lambda x:x, stemcheck=False):
        """The static method makes the exception list and returns it.

        Args:
            exceptions (:obj:`list`): The list of exception terms.
            stemf (x :obj:`str` -> y: :obj:`str`, optional): A stemmer function (default f(x) = x)
            stemcheck (:obj:`bool`, optional): if the list to be extended via the stems (default False)
            
        Returns:
            (:obj:`set`): The exception set. If stemcheck is opted both terms and their stems 
                is be represented in the list.

        """
        exceptions = set(exceptions)
        if stemcheck:
            stems = [stemf(e) for e in exceptions if e]
            exceptions.union(stems)
        return exceptions
        
        
    def isexception(self, term, exceptions=[], stemcheck=False):
        """The static makes the exception list and returns it.

        Args:
            term (:obj:`str`): The term.
            exceptions (:obj:`list`, optional): The list of exception terms (default None).
            stemcheck (:obj:`bool`, optional): if the list to be extended via the stems (default False)

        Returns:
            (:obj:`bool`): 

        """
        extended = self.exceptions.union(exceptions)
        if stemcheck:
            exceptions = self.make_exceptions(exceptions, self.stemf, stemcheck=True)
        return term in exceptions
    
    def set_exceptions(self, exceptions, stemcheck=False):
        """Sets instance-wide exception set.

        Args:
            exceptions (:obj:`list` of `str`): The list of exception terms.
            stemcheck (:obj:`bool`, optional): if the list to be extended via the stems (default False)

        Returns:
            (:obj:`bool`): True

        """
        self.exceptions = self.make_exceptions(exceptions, self.stemf, stemcheck)
        return True
        
    def reset_exceptions(self):
        """Resets the exception set to empty.

        Args:

        Returns:
            (:obj:`bool`): 

        """
        self.exceptions = set()
        return True
    
    def remove_contains(self, freq_dist, literals = tokenizer.CHARACTERS_TO_SPLIT, exceptions = []):
        """Removes the terms that contains the specific literals.
                
        Args:
            freq_dist (:obj:`nltk.FreqDist`): list of words and more.
            literals (:obj:`list` of  :obj:`str`): list of literals.
            exceptions (:obj:`list` of :obj:`str`, optional): The exception list.

        Returns:
            (:obj:`nltk.FreqDist`): Returns frequency dist.

        """
        freq_distN = copy.deepcopy(freq_dist)
        r = set(literals)
        for term in freq_dist.keys():
                if self.isexception(term, exceptions, stemcheck=True): continue
                if r.intersection(term):
                    #print(term)
                    del freq_distN[term]
        return freq_distN

