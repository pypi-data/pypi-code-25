import os
import doctest


def test_bunch():
    from huaytools.utils import bunch
    doctest.testmod(bunch)


def test_utils():
    from huaytools import utils
    doctest.testmod(utils)


def test_stopwords():
    from huaytools.nlp import stopwords
    sw_char = stopwords.stopwords_char

    from itertools import islice
    for i in islice(sw_char, 10):
        print(i)


if __name__ == '__main__':
    """"""
    # test_bunch()
    # test_utils()
    test_stopwords()