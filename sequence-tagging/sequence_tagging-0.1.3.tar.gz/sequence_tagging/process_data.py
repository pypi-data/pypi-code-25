"""Functions to read in data."""
from enum import Enum

Type = Enum("Type", "POS CHUNK ATIS")

def read_data(filename, dtype=Type.POS):
    data = []
    labels = []
    sentence = []
    sentence_labels = []
    with open(filename) as f:
        for line in f:
            if line == "\n":
                data.append(sentence)
                labels.append(sentence_labels)
                sentence = []
                sentence_labels = []
                continue
            if dtype is Type.POS or dtype is Type.ATIS:
                word, d, _ = line.split()
            elif dtype is Type.CHUNK:
                word, _, d = line.split()
            sentence.append(word)
            sentence_labels.append(d)
    return data, labels
