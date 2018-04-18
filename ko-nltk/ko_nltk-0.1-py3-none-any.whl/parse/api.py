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
class ParserI(object):
    """
    Parser Interface
    """
    @abstractmethod
    def tag(self, tokens):  
        """
        Determine the most appropriate tag sequence for the given
        token sequence, and return a corresponding list of tagged
        tokens.  A tagged token is encoded as a tuple ``(token, tag)``.
        
        :param tokens: The list of string token 
        :type tokens: list(string)
        :raises: NotImplementedError
        """
        raise NotImplementedError()