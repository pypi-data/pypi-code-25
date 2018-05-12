# -*- coding: utf-8 -*-
"""OpenMaker term scoring tools.

Author: Bulent Ozel
e-mail: bulent.ozel@gmail.com

"""

import copy
import matplotlib.pyplot as plt
import numpy as np
from numpy import log

try:
    from sklearn import linear_model
except:
    raise ImportError("Cannot import sklearn")
        
class Scoring(object):
    """The object given term frequency distribution of a foreground specific corpus and a background
    reference corpus, provides tools that help to compute specificity of each term in the foreground corpus.
    
    This kind of scoring is mainly to be used for the cases where an input text around a specific
    theme or topic is given. The process expects a tokenized, cleaned text with term counts.
    
    Note:
        It consumes a Corpus object and uses its methods and attributed and mutates it unless desired otherwise.

    Attributes:
        sCorpus (:obj:`Corpus`): A Corpus class instance of the specific corpus to be scored.
        rCorpus (:obj:`Corpus`): A Corpus class instance of the reference corpus.
        common (:obj:`list` of `str`): The common terms between the foreground and backgrouns corpus
        distinct (:obj:`list` of `str`): The terms observed in the foreground but not in the backgrouns corpus
        model: a prediction model created during instantiation process using the data of the class instance.
            For details see`form_prediction_model` method description. 
        
    """
    
    def __init__(self, sCorpus, rCorpus, nsteps = 3, mutate = False, model_threshold = 1.0):
        """The class constructor.

        Args:
            sCorpus (:obj:`Corpus`): A Corpus class instance of the specific corpus to be scored.
            rCorpus (:obj:`Corpus`): A Corpus class instance of the reference corpus.
            nsteps (:obj:`int`):  Number of phases to process at init.
                1-> raw, 2 -> raw,stem, 3 ->raw,stem,noref (default 3)
            mutate (:obj:`bool`, optional): A flag when true mutates the input Corpus object 
                for specific text corpus (default False).
            model_threshold (:obj:`float` or None) :  The minimum score value used for prediction model.
            
        """
        phase = 0
        self.model = None
        self.sCorpus = copy.deepcopy(sCorpus) if mutate else sCorpus
        self.sCorpus.labels = dict()
        self.sCorpus.scores = dict()
        self.rCorpus = rCorpus
        nt = self.sCorpus.get_count_uniques()
        self.common = self.sCorpus.intersection(rCorpus)
        print('{} / {}  raw term matches found.'.format(len(self.common), nt))
        print('Identifying specificity score for each matched terms...')
        self.compute_commons()
        self.distinct = sCorpus.difference(rCorpus)
        print('{} / {} non-raw match found.'.format(len(self.distinct), nt))
        phase += 1
        if phase >= nsteps: return
        print('Identifying specifificity score for stem matches...')
        self.compute_stem_commons()
        phase += 1
        if phase >= nsteps: return
        print('Forming prediction model for non-matching terms...')
        self.form_prediction_model(model_threshold)
        print('Computing specificity score for frequent distinct terms...')
        self.compute_distincts()
        print('All phases are done!')
        
   
    def compute_commons(self):
        """Computes the specifity score of the terms in the corpus.
        
        Note:
            It is a simple log likelihood measure. It compares frequency count of a term in
            a specific corpus versus its frequency count in the reference reference corpus.
            Here assumption is that the reference corpus is a large enough sample of the language
            at observing the occurance of a term. Then having a higher/lower observation frequency of
            a term in the specific corpus is a proxy indicator for the term choice while having a debate
            on the topic.

            The likelihood ratio for a term $P_t$ is calculated as:
            .. math::
                $P_t = log ( (ntS/NS) / (ntR/NR) )$
            
            where
                - *ntS* is the raw frequency count of the term in the entire specific corpus
                - *ntR* is the raw frequenccy count of the term in the reference corpus
                - *NS* is the total number of terms in the specific corpus
                - *NR* is the total number of terms in the reference corpus
            
            It should be noted that frequency counts are calculated after having applied the same tokenization
            and post processing such as excluding stop-words, pancuations, rare terms, etc both on the reference
            corpus and the specific corpus.
            
        Args:
            None
            
        Returns:
            (:obj:`bool`): Notifying completion of scoring.
            
        """
        for w in self.common:
            s = log(self.sCorpus.tf_dist.freq(w) / self.rCorpus.tf_dist.freq(w))
            self.sCorpus.scores[w] = s
            self.sCorpus.ref[w] = self.rCorpus.tf_dist.freq(w)
            self.sCorpus.labels[w] = 'raw'
        return True
    
    def compute_stem_commons(self):
        """Computes the specifity score of the terms in the corpus when the term as it is not 
            matched by a term in the reference corpus. It matches the stems. The loglikelihood
            ration is applied over the mean frequency counts of the matching stems.
            
            See `compute_commons` method description for details.
            
        Args:
            None
        Returns:
            (:obj:`bool`): Notifying completion of scoring.
            
        """
        matched = []
        for w in self.distinct:
            stem = self.sCorpus.stems[w]
            matches = [self.rCorpus.tf_dist.freq(w) for w,s in self.rCorpus.stems.items() if s == stem]
            if not matches: continue
            matched.append(w)
            meanw = np.mean(matches)
            s = log(self.sCorpus.tf_dist.freq(w) / meanw)
            self.sCorpus.scores[w] = s
            self.sCorpus.labels[w] = 'stem' 
            self.sCorpus.ref[w] = meanw
        print('{} stems matched.'.format(len(matched)))
        self.distinct = list(set(self.distinct).difference(set(matched)))
        return True
    
    
    def compute_distincts(self):
        """Computes the specifity score of the terms in the corpus when neither the term nor its stems
            matched by the background corpus.
            
        Note:
            It uses a log linear regression model to predict likelihood of the dictinct terms.
            The model is trained using the scores and frequencies within the matching set.
            
            See `form_prediction_model` method description for details.
            
        Args:
            None
        Returns:
            (:obj:`bool`): Notifying completion of scoring.
            
        """
        for w in self.distinct:
            f = self.sCorpus.tf_dist[w]
            s = self.predict(w,f)
            self.sCorpus.scores[w] = s
            self.sCorpus.ref[w] = None
            self.sCorpus.labels[w] = 'noref'
        return True
    
        
    def form_prediction_model(self, threshold = 1.0):
        """The method creats the prediction model to be used for distinct terms.
            
        Note:
            It is based on a log-linear regression. The model is created using the observed
            scores and frequencies within the matching set. The model aims to fit a best line
            to logarithm of the observed term frequencies vs associated scores.
            
            Considering the fact that frequent distinct terms are likely among the ones with a 
            higher specificity, the terms with relatively high scores are used for the regression.
            The R-squared of the regression tests have been used for validation of the approach.
            In the same reasoning among the all distinct terms the ones with relatively higher frequencies
            are considered for scoring.
            
        ToDo:
            As a second approach, the model training to be improved considering terms with relatively high term
            frequencies and high specificity scores. Observe the scatter plots for the insight.
            
            An alternative, a third approach, would be forming the logarithmic bins on frequencies and using
            distributional charcteristics of each bin at making predictions. For instance, by simply predicting
            the median value as the guess. 
            
        Args:
            threshold (:obj:`float`, optional):  The default value is driven from regression tests on 
                test cases (default 1.0).
                
        Returns:
            (:obj:`bool`): Notifying completion of scoring.
            
        """
        print('The minimum score used for the modelling = {}'.format(threshold))
        distro = self._get_distro(threshold = threshold)
        x = distro['x']
        y = distro['y']
        if not x or not y: return False
        xa = np.asarray(x)
        lm = linear_model.LinearRegression()
        self.model = lm.fit(xa.reshape(-1,1),y)
        return True
    
    
    def _get_distro(self, threshold= 1.0, islog = True):
        """The method retrieves frequency and score distributions for the terms with a computed score.
                        
        Args:
            threshold (:obj:`float`, optional):  The default value is driven from regression tests on 
                test cases (default 1.0).
            
            islog (:obj:`bool`): Whether natural log of the frequency counts to be returned (default True).
                
        Returns:
            (:obj:`dict`): 'x' holds frequency counts, 'y' holds scores .
            
        """
        x = list()
        y = list()
        for w in self.sCorpus.scores.keys():
            s = self.sCorpus.scores[w]
            if s is None: continue
            if threshold:
                if s < threshold: continue
            y.append(s)
            if islog:
                x.append(log(self.sCorpus.tf_dist[w]))
            else:
                x.append(self.sCorpus.tf_dist[w])
        return {'x':x, 'y':y}
    
    
    def plot(self, threshold= 1.0, islog = True):
        """Scatter plot of frequency vs scores.
                        
        Args:
            threshold (:obj:`float`, optional):  The default value is driven from regression tests on 
                test cases (default 1.0).
            
            islog (:obj:`bool`): Whether natural log of the frequency counts to be returned (default True).
                
        Returns:
            (:obj:`bool`): True.
            
        """
        distro = self._get_distro(threshold, islog)
        x = distro['x']
        y = distro['y']
        plt.scatter(x,y)
        plt.show()
        return True
        

    def predict(self, w, count, minp = 0.001, minf = 3):
        """The method assigns a predicted score to a given term with a a frequency
            over the designated threshold. An internally formed prediction model is used.
            The natural logorithm of raw frequency counts is passed to the model. See 
            `form_prediction_model` method description for details.
            
        Args:
            count (:obj:`int`): The raw frequency count.
            minp (:obj:`float`, optional): The relative frequency threshold (default 0.001).
            minf (:obj:`int`, optional): The raw frequency threshold (default 3).
                
        Returns:
            (:obj:`float`): The predicted score.
            
        """
        if not self.model: return None
        if count < minf: return None
        if self.sCorpus.tf_dist.freq(w) < minp: return None
        return self.model.predict(log(count))[0]
   

    def get_scores_by(self, stype='raw'):
        """The method returns computed/available scores by the label of the terms.
        
        Note:
            The labels in this implementation correspond:
            - raw: the term as it is was identified in the background corpus, so
                a loglikelihood scoring was applied
            - stem: not the term as it is but its stem was identified, so mean of the observed
                stem occurances in the background was used as the reference
            - noref: neither the term nor its stem was identified, so the prediction model was used
                for the frequent ones.
            
        Args:
            stype (:obj:`str`, optional): The term scoring type (default 'raw').
                
        Returns:
            (:obj:`dict`): The term scores.
            
        """
        return {w:self.sCorpus.scores[w] for w,t in self.sCorpus.labels.items() if t == stype}
