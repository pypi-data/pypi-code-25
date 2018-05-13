# -*- coding: utf-8 -*-
"""
Human word indexes

TODO: Add vocabulary caching for large indexes
"""

import logging
from tqdm import tqdm
from nltk.corpus import words
from functools import reduce
import pandas as pd
import numpy as np
from human_word_indexes.word_index_filter import WordIndexFilter

logger = logging.getLogger(__name__)


class WordIndexGenerator:
    def __init__(self, length, word_count=3, word_filter='default', sep='.', custom_corpus=None):
        '''
        Create an instance of a Word Index, NLTK corpuses must be installed with the nltk.download() function

        :param custom_corpus: A list of words for a custom index corpus
        :type custom_corpus: list
        :param length: The length of the index to generate
        :type length: int
        :param word_count: The number of words per index record - 3    words gives you 'safe.cow.thespian'
        :type word_count: int
        :param word_filter: Use the default word filter or pass an instance of WordIndexFilter
        :type word_filter: WordIndexFilter
        :param sort: Should the word index be sorted along its words (useful for incrementally changing data)
        :type sort: bool
        :param sep: Word separator character
        :type sep: str
        '''
        self.custom_corpus = custom_corpus
        if self.custom_corpus:
            logger.info('Custom corpus specified')
            if type(self.custom_corpus) != list:
                raise ValueError('Custom corpus must be list of strings')
        if word_filter == 'default':
            self.word_filter = WordIndexFilter().filter_word
        else:
            if type(word_filter) != WordIndexFilter:
                raise ValueError('Please specify a valid WordIndexFilter class')
            self.word_filter = word_filter.filter_word
        logger.info('Building index vocabulary')
        self._max_records = None
        self._length = length
        self._words = word_count
        self._sep = sep
        self._build_vocabulary()

    def generate_word_index(self, sort=True):
        '''
        Generates and returns the word index

        :param sort: should the returned index be sorted?
        :type sort: bool
        :return: Pandas wordindex series
        :rtype Series
        '''
        ind = pd.DataFrame(np.random.choice(self._filtered_list, (self._length, self._words), True)).drop_duplicates()
        if sort:
            ind.sort_values(by=list(ind.columns), inplace=True)
        ind = ind.apply(self._combine_words, axis=1).reset_index(drop=True)
        return ind

    def _build_vocabulary(self):
        self.raw_word_list = []
        for i in tqdm(self.custom_corpus or words.words()):
            self.raw_word_list.append(i.lower())
        logger.info('Vocabulary words loaded: ' + str(len(self.raw_word_list)))
        self._filtered_list = [i for i in filter(self.word_filter, self.raw_word_list)]
        logger.info('Filtered word list length: ' + str(len(self._filtered_list)))
        self._max_records = len(self._filtered_list) ** self._words
        if self._length > self._max_records:
            raise RuntimeError('Desired record count exceeds vocabulary length'
                               ', define looser word filters or increase word counts')

    def _combine_words(self, l):
        return reduce((lambda x, y: x + self._sep + y), l)
