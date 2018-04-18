# -*- coding:utf8 -*-
# Korean Natural Langugae Toolkit : Tokenizer Interfaces
#
# Copyright (C) 2017 - 0000 KoNLTK project 
# Author: HyunYoung Lee <hyun02.engineer@gmail.com>
#         GyuHyeon Nam <ngh3053@gmail.com>
#         Younghun Cho <cyh905@gmail.com>        
#         Seungshik Kang <sskang@kookmin.ac.kr>
# URL: <http://www.konltk.org>
# For license information, see LICENSE.TXT


from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class TokenizerI(object):
    """
    Tokenizer Interface
    """
    @abstractmethod
    def tokenize(self, string):
        """ 
        Return a tokenized copy of string. 
        
        :param string: string to tokenize
        :type string: str
        :raises: NotImplementedError
        """
        raise NotImplementedError()


class SimpleTokenizer(TokenizerI):
    def tokenize(self, string):
        return string.split()
