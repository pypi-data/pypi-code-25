# Korean Natural Language Toolkit: Tokenizer Interface
# 
# Author: <@gmail.com>
#
# Contributors: 
# URL: <http://konltk.org/>
# For license information, see LICENSE.TXT

from abc import ABCMeta, abstractmethod
from six import add_metaclass

from konltk.parse.api import ParserI


@add_metaclass(ABCMeta)
class ChunkParserI(ParserI):
    """
    ChunkParser Interface
    """
    @abstractmethod
    def parse(self, tokens):
        """
        Return the best chunk structure for the given tokens
        and return a tree.

        :param tokens: The list of (word, tag) tokens to be chunked.
        :type tokens: list(tuple)
        :rtype: Tree
        """
        raise NotImplementedError()
