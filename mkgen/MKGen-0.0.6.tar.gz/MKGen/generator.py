import numpy as np
import pickle
import sys
import os
from MKGen import settings


def generate(word, model, num_of_words=30):
    """
    :param (str) word:
    :param (dict) model:
    :param (int) num_of_words:
    :return (str) result:
    """
    if word not in model.keys():
        start_words = list(model['START'].keys())
        next_word = np.random.choice(start_words)
    else:
        next_word = word
    sent = []
    sent.append(next_word)
    for i in range(num_of_words):
        if next_word == 'END':
            break
        expected = model[next_word].weighted_random_word()
        sent.append(expected)
        next_word = expected
    result = ''.join(sent)
    result = result.rstrip('END')
    return result


if __name__ == '__main__':
    try:
        name = sys.argv[1]
        word = sys.argv[2]
    except IndexError:
        name = 'asuka'
        word = '遊び'
    file = name + '.pkl'
    input_path = os.path.join(settings.MODEL_DIR, file)
    with open(input_path, 'rb') as f:
        model = pickle.load(f)
    sentence = generate(word, model, num_of_words=140)
    print(sentence)
