# -*- coding:utf8 -*-
# Korean Natural Langugae Toolkit : Tagger Interfaces
#
# Copyright (C) 2017 - 0000 KoNLTK project 
# Author: HyunYoung Lee <hyun02.engineer@gmail.com@gmail.com>
#         GyuHyeon Nam <ngh3053@gmail.com>
#         Younghun Cho <cyh905@gmail.com>        
#         Seungshik Kang <sskang@kookmin.ac.kr>
# URL: <http://www.konltk.org>
# For license information, see LICENSE.TXT

from abc import ABCMeta, abstractmethod
from six import add_metaclass


@add_metaclass(ABCMeta)
class TaggerI(object):
    """
    Tagger Interface
    """
    @abstractmethod
    def tag(self, tokens):  
        """
        Determine the most appropriate tag sequence for the given
        token sequence, and return a corresponding list of tagged
        tokens.  A tagged token is encoded as a tuple ``(token, tag)``.

        :param tokens: [description]
        :type tokens: [type]
        :raises: NotImplementedError
        """
        raise NotImplementedError()
