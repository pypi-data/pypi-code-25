# Korean Natural Language Toolkit: Tokenizer Interface
# 
# Author: <@gmail.com>
#
# Contributors: 
# URL: <http://konltk.org/>
# For license information, see LICENSE.TXT

from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class StemmerI(object):
    """
    Stemmer Interface
    """
    @abstractmethod
    def stem(self, token):
        """
        Strip affixes from the token and return the stem.

        :param token: The token that should be stemmed.
        :type token: str
        """
        raise NotImplementedError()


class SimpleStemmer(StemmerI):
    def stem(self, token):
        if token[-1] in "은는이가을를":
            return token[:-1]
        else:
            return token
