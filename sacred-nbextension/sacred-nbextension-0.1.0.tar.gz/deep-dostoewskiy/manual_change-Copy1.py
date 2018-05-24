
# coding: utf-8

# In[ ]:

import pandas as pd
from conllu.parser import parse, parse_tree
from nltk.parse import DependencyGraph
import numpy as np

from IPython.display import HTML
from pymorphy2 import MorphAnalyzer
from russian_tagsets import converters

analyzer = MorphAnalyzer()
ou = converters.converter(u'opencorpora-int', u'ud20')


# In[3]:

df = pd.read_pickle('demons-ext.pkl')


# In[ ]:

' '.join(df[df.n_sent == 15].token)
' '.join(df[df.n_sent == 15].POS)
' '.join(df[df.n_sent == 15].Penn_POS.fillna('X'))


# In[ ]:

for i in range(100, 130 ,5):
    print(' '.join(df[df.n_sent == i].token))
    print(' '.join(df[df.n_sent == i].POS))
    print(' '.join(df[df.n_sent == i].dep))
    print(' ')


# In[34]:


i = 125
sent = df[df.n_sent == i]

connl = sent.drop('n_sent', axis=1).to_csv(header=False, index=False, sep='\t', encoding='utf-8')
# parse(connl)
dg = DependencyGraph(connl.decode('utf-8'))
tree = dg.tree()

print(' '.join(sent.token))
print(' '.join(sent.POS))
print(' '.join(sent.dep))
tree.pprint()

# HTML(dg._repr_svg_().split('\\n')[0])


# In[20]:

df.groupby('morph').count()[['n_token']].sort('n_token', ascending=False)


# In[40]:

target_word = sent[sent.token == u'складывала']
morph = target_word.morph.values[0]


# In[183]:

def ud_to_od(ud):
    # http://opencorpora.org/dict.php?act=gram
    
    from conllu.parser import parse_dict_value
    
    ud_to_od = {
        'Gender': {
            'Fem': 'femn',
            'Masc': 'masc',
            'Neut': 'neut'
        },
        'Number': {
            'Plur': 'plur',
            'Sing': 'sing'
        },
        'Aspect': {
            'Imp': 'impf'
        }, 
        'Tense': {
            'Past': 'past',
            'Pres': 'pres'
        },
        'Case': {
            'Gen': 'gent',
            'Nom': 'nomn',
            'Dat': 'datv',
            'Acc': 'accs',
            'Ins': 'ablt',
            'Loc': 'loct'
        },
        'Animacy': {
            'Inan': 'inan'
        },
        'Person': {
            '3': '3per'
        }
    }
    
    morph_dict = parse_dict_value(ud)
    print(ud)
    coded = []
    for feat in ud_to_od.keys():
        value = morph_dict.get(feat, None)
        if value:
            coded.append(ud_to_od[feat].get(value, '--'))
    return coded



def transfer_morph(source, target):
    target = analyzer.parse(target)[0]
    if type(source) == (unicode or str):
        source = analyzer.parse(source)[0]

        source_pos = source.tag.POS
        target_pos = target.tag.POS
        if source_pos == 'INFN':
            source_pos = 'VERB'
        if target_pos == 'INFN':
            target_pos = 'VERB'

        assert  source_pos == target_pos,  "source and target POS should be the same"
            
        source_morph = str(source.tag).split(',')
        source_morph = [f.split()[-1] for f in source_morph]
        
    elif type(source) == list:
        source_morph = source

#     print(source_morph)
    
    return target.inflect(source_morph).word

for w in [u'чашка', u'телефон', u'зеркало']:
    print transfer_morph(u'сна', w)

for w in [u'убирать', u'прятать', u'скрывать']:
    print transfer_morph(u'читала', w)
    print transfer_morph(u'рисовало', w)
    print transfer_morph(['plur', 'past'], w)


# In[182]:

od = ud_to_od(df.iloc[37].morph)
od
print(transfer_morph(od, u'стоять'))


# In[134]:

a = analyzer.parse(u'идти')[0]
a.inflect(['plur'])


# In[173]:


# for lexeme in analyzer.parse(u'ваш')[0].lexeme:
#     print(lexeme.word)
#     print(lexeme.tag)
#     pos, feats = ou(str(lexeme.tag)).split()
#     print(feats)
#     print(morph)
    


# In[32]:

# token = 'привычка'

def get_new_word(morph):
    other_ws = df[df.morph == morph]
    new_word = other_ws.iloc[i]
    new_word.to_frame().T
    return new_word

dep = 'dobj'
w = sent[sent.dep == dep]
w = sent[sent.token == 'складывала']
morph = w['morph'].values[0]

new_sent = sent.copy()
new_sent.loc[new_sent.dep == dep, 'token'] = new_word.token
new_sent


# In[123]:

import pymorphy2
analyzer = pymorphy2.MorphAnalyzer()


# In[ ]:




# In[42]:

w = analyzer.parse('стол')[0]
w.inflect({})

