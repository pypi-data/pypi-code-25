import random
import numpy as np


def create_corpus(sent, current_next):
    """
    :param (list) sent:
    :return (dict) current_text:
    """
    for i, word in enumerate(sent):
        maxlen = len(sent)
        if i == 0:
            next_word = sent[i + 1]

            if 'START' not in current_next.keys():
                current_next['START'] = Dictogram()

            if next_word not in current_next['START'].keys():
                current_next['START'][next_word] = 1
            else:
                current_next['START'][next_word] += 1

        elif i == maxlen - 1:
            this_word = sent[i]

            if this_word not in current_next.keys():
                current_next[this_word] = Dictogram()

            if 'END' not in current_next[this_word].keys():
                current_next[this_word]['END'] = 1
            else:
                current_next[this_word]['END'] += 1

        elif i < maxlen - 1:
            this_word = sent[i]
            next_word = sent[i + 1]

            if this_word not in current_next.keys():
                current_next[this_word] = Dictogram()

            if next_word not in current_next[this_word].keys():
                current_next[this_word][next_word] = 1
            else:
                current_next[this_word][next_word] += 1

    return current_next


class Dictogram(dict):

    def random_word(self):
        """適当なキーを一つ返す"""
        return random.sample(self.keys(), 1)[0]

    def weighted_random_word(self):
        """重みに基づいてランダムなキーを一つ返す"""
        keys = [key for key in self.keys()]
        values = [value for value in self.values()]
        weight = [v/sum(values) for v in values]

        return np.random.choice(keys, p=weight)


