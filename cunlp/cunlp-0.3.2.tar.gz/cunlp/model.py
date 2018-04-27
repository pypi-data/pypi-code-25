import warnings
warnings.filterwarnings("ignore")

from keras.models import Sequential
from keras.layers import Dense, GRU, Embedding, Bidirectional, TimeDistributed, Dropout
from keras.optimizers import Adam
import numpy as np
import os, pickle

# Private Zone
_CHARS = [
  '\n', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+',
  ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8',
  '9', ':', ';', '<', '=', '>', '?', '@', 'A', 'B', 'C', 'D', 'E',
  'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
  'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_',
  'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
  'n', 'o', 'other', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
  'z', '}', '~', 'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช',
  'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ', 'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท',
  'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ', 'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ฤ',
  'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ', 'ฯ', 'ะ', 'ั', 'า',
  'ำ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'ฺ', 'เ', 'แ', 'โ', 'ใ', 'ไ',
  'ๅ', 'ๆ', '็', '่', '้', '๊', '๋', '์', 'ํ', '๐', '๑', '๒', '๓',
  '๔', '๕', '๖', '๗', '๘', '๙', '‘', '’', '\ufeff'
]
_CHARS_MAP = {v: k for k, v in enumerate(_CHARS)}

def _load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

# Tokenizer Model
def _get_tokenizer_model():
    model_tokenizer = Sequential()
    model_tokenizer.add(Embedding(len(_CHARS)+1, 32))
    model_tokenizer.add(Bidirectional(GRU(32)))
    model_tokenizer.add(Dense(100, activation='relu'))
    model_tokenizer.add(Dense(1, activation='sigmoid'))
    model_tokenizer.compile(optimizer=Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    return model_tokenizer

def _map_sentence(sentence):
    mapped = []
    for char in sentence:
        if char in _CHARS_MAP:
            mapped.append(_CHARS_MAP[char])
        else:
            mapped.append(_CHARS_MAP['other'])
    return mapped

def _prepare_data(sentence):
    sentence = _map_sentence(sentence)
    ready_to_feed = []
    for i in range(len(sentence)):
        mini_batch = sentence[i+1:i+11]
        mini_batch.extend([1]*(10-len(mini_batch)))
        added_right = 0
        j = i-1
        while j >= 0 and added_right < 10:
            mini_batch.append(sentence[j])
            added_right += 1
            j -= 1
        mini_batch.extend([1]*(10 - added_right))
        mini_batch.append(sentence[i])
        ready_to_feed.append(mini_batch)
    return np.array(ready_to_feed)

def _to_string(sentence, classes):
    output = ''
    for i in range(len(sentence)):
        if(classes[i] == 1 and i != 0):
            output += '|'
        output += sentence[i]
    return output

global _tokenizer_model
_tokenizer_model = _get_tokenizer_model()
_tokenizer_model.load_weights(os.path.dirname(os.path.abspath(__file__)) + '/_model_tokenizer')

# POS Tagger Model
def _get_pos_model():
    model_pos = Sequential()
    model_pos.add(Embedding(100001, 50, input_length=102, mask_zero=True))
    model_pos.add(Bidirectional(GRU(32, return_sequences=True)))
    model_pos.add(Dropout(0.2))
    model_pos.add(TimeDistributed(Dense(48, activation='softmax')))
    model_pos.compile(optimizer=Adam(),  loss='categorical_crossentropy', metrics=['categorical_accuracy'])
    return model_pos

global _word_to_idx
global _idx_to_pos
_model_pos_map = _load(os.path.dirname(os.path.abspath(__file__)) + '/_model_pos_map')
_word_to_idx = _model_pos_map[0]
_idx_to_pos = _model_pos_map[1]
del _model_pos_map

def _pos_word_to_idx(word_list):
    feed = []
    for word in word_list:
        if word in _word_to_idx:
            feed.append(_word_to_idx[word])
        else:
            feed.append(_word_to_idx['UNK'])
    while len(feed) < 102:
        feed.append(0)
    return np.array([feed[:102]])

def _pos_idx_to_pos(classes, length):
    pos = []
    for c in classes[:length]:
        if c in _idx_to_pos:
            pos.append(_idx_to_pos[c])
        else:
            pos.append('UNK')
    return pos

global _pos_model
_pos_model = _get_pos_model()
_pos_model.load_weights(os.path.dirname(os.path.abspath(__file__)) + '/_model_pos')

# Public Zone
def tokenize(sentence, listing=True):
    if len(sentence) == 0:
        if not listing:
            return ''
        return []
    results = _to_string(sentence, _tokenizer_model.predict_classes(_prepare_data(sentence)))
    if not listing:
        return results
    return results.split('|')

def pos(tokens):
    if len(tokens) == 0:
        return []
    results = []
    for i in range(0, len(tokens), 102):
        batch = tokens[i:i+102]
        ready_to_feed = _pos_word_to_idx(batch)
        results.extend(_pos_idx_to_pos(_pos_model.predict_classes(ready_to_feed)[0], len(batch)))
    return results