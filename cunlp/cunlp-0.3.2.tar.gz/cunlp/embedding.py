from os import path
from math import sqrt
from pickle import load
from itertools import groupby
from re import match
from operator import mul, itemgetter
import numpy as np
import random

# Private zone
def _load(path):
    with open(path, 'rb') as f:
        return load(f)

global _embeddings
global _vocab_string
_embeddings, _vocab_string = _load(path.dirname(path.abspath(__file__)) + '/_embedding')

global _number_regex
_number_regex = "^[0-9,๐-๙]+$"

def _dot_product(v1, v2):
    return sum(map(mul, v1, v2))

def _cos_sim(v1, v2):
    prod = _dot_product(v1, v2)
    len1 = sqrt(_dot_product(v1, v1))
    len2 = sqrt(_dot_product(v2, v2))
    return prod / (len1 * len2)
  
def _contain_Thai(str):
    for chr in str:
        cVal = ord(chr)
        if cVal >= 3584 and cVal <= 3711:
            return True
    return False

def _build_suffix_array(long_str):
    size = len(long_str)
    step = min(16, size)
    SA = list(range(size))
    SA.sort(key=lambda x: long_str[x:x+step])

    grpstart = size * [False] + [True]
    RSA = size * [None]

    stgrp, igrp = '', 0
    for i, pos in enumerate(SA):
        st = long_str[pos:pos + step]
        if st != stgrp:
            grpstart[igrp] = (igrp < i - 1)
            stgrp = st
            igrp = i
        RSA[pos] = igrp
        SA[i] = pos

    grpstart[igrp] = (igrp < size - 1 or size == 0)
    while grpstart.index(True) < size:
        nextgr = grpstart.index(True)
        while nextgr < size:
            igrp = nextgr
            nextgr = grpstart.index(True, igrp + 1)
            glist = []
            for ig in range(igrp, nextgr):
                pos = SA[ig]
                if RSA[pos] != igrp:
                    break
                newgr = RSA[pos + step] if pos + step < size else -1
                glist.append((newgr, pos))
            glist.sort()
            for ig, g in groupby(glist, key=itemgetter(0)):
                g = [x[1] for x in g]
                SA[igrp:igrp + len(g)] = g
                grpstart[igrp] = (len(g) > 1)
                for pos in g:
                    RSA[pos] = igrp
                igrp += len(g)
        step *= 2
    del grpstart

    LCP = size * [None]
    h = 0
    for i in range(size):
        if RSA[i] > 0:
            j = SA[RSA[i] - 1]
            while i != size - h and j != size - h and long_str[i + h] == long_str[j + h]:
                h += 1
            LCP[RSA[i]] = h
            if h > 0:
                h -= 1
    if size > 0:
        LCP[0] = 0
    return SA, LCP

def _find_lcs_pos(sa, lcp, mark, word):
    lcs_pos = [0,0,0,0]
    lcs_length = 0
    lcs_score = 0
    w_length = len(sa)-mark
    score = [i for i in range(w_length+1, 1, -1)]
    if w_length >= 5:
        score[0] += w_length+1

    for i in range(len(lcp)):
        if lcp[i] >= lcs_length:
            pos = []
            if sa[i] < mark and sa[i-1] >= mark:
                pos = [sa[i],sa[i]+lcp[i],sa[i-1]-mark,sa[i-1]-mark+lcp[i]]
            elif sa[i] >= mark and sa[i-1] < mark:
                pos = [sa[i-1],sa[i-1]+lcp[i],sa[i]-mark,sa[i]-mark+lcp[i]]
            if pos == [] or _vocab_string[pos[0]] in 'ุูึๆำะัํี๊ฯ้็่๋าิื์':
                continue
            sub_score = sum(score[pos[2]:pos[3]])
            if lcs_length == 0:
                lcs_pos = pos
                lcs_length = lcp[i]
                lcs_score = sub_score
            elif lcs_score <= sub_score:
                lcs_pos = pos
                lcs_length = lcp[i]
                lcs_score = sub_score
    return lcs_pos

def _generate_random_vector(dimension, start, end):
    vector = []
    for _ in range(dimension):
        vector.append(np.float32(random.uniform(start, end)))
    return np.array(vector)

# Public zone
def get_embeddings():
    return _embeddings

def substitute(word):
    if len(word) == 0:
        return '<unk>'
    sa, lcp = _build_suffix_array(_vocab_string + word)
    vocab_string_length = len(_vocab_string)
    a, b, c, d = _find_lcs_pos(sa, lcp, vocab_string_length, word)
    sub_word = word[c:d]
    if sub_word in _embeddings:
        return sub_word
    if d-c >= 2:
        a -= 1
        while a >= 0:
            if _vocab_string[a] == chr(0):
                break
            sub_word = _vocab_string[a] + sub_word
            a -= 1
        while b < vocab_string_length:
            if _vocab_string[b] == chr(0):
                break
            sub_word += _vocab_string[b]
            b += 1
        return sub_word
    return '<unk>'
    
def vectorize(raw_word, sub=False):
    if len(raw_word) == 0:
        return _embeddings['<unk>']
    word = raw_word.lower().strip()
    if  bool(match(_number_regex, word)):
        return _embeddings['<number>']
    elif word in _embeddings:
        return _embeddings[word]
    else:
        if sub:
            return _embeddings[substitute(word)]
        return _embeddings['<unk>']

def vectorize_in_depth(raw_word, sub=False):
    if len(raw_word) == 0:
        return ('<unk>', _embeddings['<unk>'])
    word = raw_word.lower().strip()
    if  bool(match(_number_regex, word)):
        return ('<number>', _embeddings['<number>'])
    elif word in _embeddings:
        return (word, _embeddings[word])
    else:
        if sub:
            sub_word = substitute(word)
            return (sub_word, _embeddings[sub_word])
        return ('<unk>', _embeddings['<unk>'])

def sentence_vectorize(tokens, sub=False):
    sent_vec = vectorize(tokens[0], sub)
    for remains in tokens[1:]:
        sent_vec += vectorize(remains, sub)
    return sent_vec

def compare_similarity(w1, w2, sub=False):
    if type(w1) is str:
        w1 = vectorize(w1, sub)
    elif type(w1) is list:
        w1 = sentence_vectorize(w1, sub)
    if type(w2) is str:
        w2 = vectorize(w2, sub)
    elif type(w2) is list:
        w2 = sentence_vectorize(w2, sub)
    return abs(_cos_sim(w1, w2))

def most_similarity(word, rank=3, sub=False, eng=False):
    selected = []
    rank = max(1, rank)
    if not _contain_Thai(word):
        eng = True
    if type(word) is str:
        may_be_sub, word_vector = vectorize_in_depth(word, sub)
        if may_be_sub == '<unk>':
            return [('<unk>',1.0)]*rank
    else:
        word_vector = word
        may_be_sub = word
    for vocab in _embeddings:
        if not eng and not _contain_Thai(vocab):
            continue
        if vocab == may_be_sub:
            continue
        similarity_score = abs(_cos_sim(word_vector,_embeddings[vocab]))
        if len(selected) < rank:
            selected.append((vocab, similarity_score))
            selected = sorted(selected, key=lambda x: x[1], reverse=True)
        else:
            i = rank-1
            while i > 0:
                if similarity_score >= selected[i][1]:
                    i -= 1
                    selected[i+1] = selected[i]
                else:
                    break
            if i == rank-1:
                continue
            if similarity_score >= selected[0][1]:
                selected[i] = (vocab, similarity_score)
            else:
                selected[i+1] = (vocab, similarity_score)
    return selected

def initiate_embeddings(word_list, sub=False):
    embeddings_return = []
    for word in word_list:
        if word in _embeddings:
            embeddings_return.append(_embeddings[word])
        elif sub:
            embeddings_return.append(vectorize(word, sub))
        else:
            embeddings_return.append(_generate_random_vector(100, -3.5, 3.5))
    return embeddings_return