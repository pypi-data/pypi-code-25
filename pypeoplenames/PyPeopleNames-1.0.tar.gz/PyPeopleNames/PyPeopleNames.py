import nltk
import sys
import os
import enchant
from nltk.corpus import stopwords

#Find names using NLTK

def countNames(text): # now 20x faster! BUGS: Locations not returning properly
    sys.stdout = open(os.devnull, "w") #Stop NLTK download printing to console
    nltk_sets = ['corpora/stopwords', 'corpora/words', 'chunkers/maxent_ne_chunker',
                      'taggers/averaged_perceptron_tagger', 'tokenizers/punkt']
    for sets in nltk_sets:
        nltk.download(sets.split('/')[1]) #Download/check download of required NLTK packages

    d = enchant.Dict("en_US")
    s = set(stopwords.words('english'))
    sys.stdout = sys.__stdout__
    locations = []
    tokens = nltk.tokenize.word_tokenize(text)
    pos = nltk.pos_tag(tokens)
    sentt = nltk.ne_chunk(pos, binary=False)
    names = []
    person = []
    name = ""
    for subtree in sentt.subtrees(filter=lambda t: t.label() == 'PERSON'):
        for leaf in subtree.leaves():
            person.append(leaf[0])
        if 1 < len(person) < 3 and len(person[1]) > 2:  # avoid grabbing lone surnames
            firstname_caps = person[0]
            firstname = firstname_caps.lower()
            firstname_dict = str(d.check(firstname))
            firstname_singular_dict = "False"
            if person[0][-1:] == "s":
                firstname_singular = firstname.replace(' ', '')[:-1]
                firstname_singular_dict = str(d.check(firstname_singular))
            if firstname_dict == "False" and firstname_singular_dict == "False" and firstname_caps.isupper() == False and str(person[1]).isupper() == False:
                for part in person:
                    name += part + ' '
                if name[:-1] not in names:
                    names.append(name[:-1])
                    location = text.lower().find(name[:-1].lower())
                    locations.append(location)
                name = ''
        person = []
    return names