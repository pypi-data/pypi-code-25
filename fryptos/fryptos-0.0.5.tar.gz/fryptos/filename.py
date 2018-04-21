"""File name operation.

Change file name for encryption.
"""

import random

WORDS = ('abcdefghijkmnopqrstuvwxyz'
         'ABCDEFGHIJKLMNPQRSTUVWXYZ123456789'
         '_-')


def change(filename, min_word=5, max_word=10, min_class=3, max_class=6):
    """Change directry name."""
    extention = ""
    if '.' in filename:
        extention = filename.split('.')[-1]
    dir_class_len = random.randint(min_class, max_class)
    dir_names = []
    for n in range(dir_class_len):
        dir_names.append(_generate_random(min_word, max_word))
    return '/'.join(dir_names) + '.' + extention


def _generate_random(min_word=5, max_word=10):
    """Generate random string.

    >> _generate_random(5, 10) == _generate_random(5, 10)
    False
    """
    word_len = random.randrange(min_word, max_word)
    word = ""
    for n in range(word_len):
        word_num = random.randint(0, int(len(WORDS)) - 1)
        word += WORDS[word_num]
    return word

if __name__ == '__main__':
    ds = []
    for n in range(10000):
        d = change('hoge.png',
                   min_word=7,
                   max_word=13,
                   min_class=4,
                   max_class=7)
        if d in ds:
            raise ValueError('duplication dir')
        ds.append(d)
