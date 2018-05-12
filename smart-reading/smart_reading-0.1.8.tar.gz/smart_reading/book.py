import nltk
from nltk import sent_tokenize,word_tokenize,pos_tag
from nltk.chunk import ne_chunk

import regex
from os import path

from matplotlib import pyplot as plt
import numpy as np

class Book:
    
    def __init__(self, filename):
        if filename.endswith('.txt'):
            with open(filename) as f:
                text = regex.sub(' ?{[0-9]+} ?',' ',f.read())
            
            self.raw = text
            self.sents = [sent.replace('\n',' ') for sent in sent_tokenize(text)]
            self.tokens = word_tokenize(text)
            self.tagged = pos_tag(self.tokens)
            self.entities = ne_chunk(self.tagged)
            self.NE = [child for child in self.entities if type(child) == nltk.tree.Tree]
            self.Text = nltk.Text(self.tokens)
        else:
            raise TypeError('Extension {} not supported.'.format(path.splitext(filename)[1]))
        
def sample():
    here = path.abspath(path.dirname(__file__))
    print(here)
    return Book(path.join(here,'Benn_ch_II.txt'))