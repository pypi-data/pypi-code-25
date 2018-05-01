# Copyright 2018 The NLP Odyssey Authors.
# Copyright 2018 Marco Nicola <marconicola@disroot.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module providing the :class:`.EmptyNode` class."""

from typing import Optional
from colonel.base_rich_sentence_element import BaseRichSentenceElement

__all__ = ['EmptyNode']


class EmptyNode(BaseRichSentenceElement):
    """Representation of an *Empty Node* sentence element"""

    __slots__ = ('main_index', 'sub_index')

    def __init__(
            self,
            main_index: Optional[int] = None,
            sub_index: Optional[int] = None,
            **kwargs
    ) -> None:
        super(EmptyNode, self).__init__(**kwargs)

        #: The primary index of the empty node.
        #:
        #: This usually corresponds to the value of the :attr:`.Word.index`
        #: after which the empty node is inserted, or to zero (``0``) if the
        #: empty node is inserted before the first word of the sentence (the
        #: one with *index* equal to ``1``).
        #:
        #: It is compatible with *CoNLL-U* ``ID`` field, which in case of an
        #: empty node is a decimal number: the *main index* here corresponds
        #: to the integer part of such value.
        self.main_index: Optional[int] = main_index

        #: The secondary index of the empty node.
        #:
        #: It is compatible with *CoNLL-U* ``ID`` field, which in case of an
        #: empty node is a decimal number: the *sub index* here corresponds
        #: to the decimal part of such value.
        self.sub_index: Optional[int] = sub_index

    def is_valid(self) -> bool:
        """Returns whether or not the object can be considered valid,
        however ignoring the context of the sentence in which the word
        itself is possibly inserted.

        In compliance with the *CoNLL-U* format, an instance of type
        :class:`.EmptyNode` is considered valid only when :attr:`main_index` is
        set to a value equal to or greater than zero (``0``) **and**
        :attr:`sub_index` is set to a value greater than zero (``0``).
        """
        return super(EmptyNode, self).is_valid() and \
            self.main_index is not None and self.main_index >= 0 and \
            self.sub_index is not None and self.sub_index > 0

    def to_conllu(self) -> str:
        """Returns a *CoNLL-U* formatted representation of the element.

        No validity check is performed on the attributes; values not compatible
        with *CoNLL-U* format could lead to an incorrect output value or
        raising of exceptions.
        """
        return '\t'.join([
            f'{self.main_index}.{self.sub_index}',
            self.form or '_',
            self.lemma or '_',
            self.upos.name if self.upos else '_',
            self.xpos or '_',
            self._feats_to_conllu(),
            '_',  # Head
            '_',  # DepRel
            self._deps_to_conllu(),
            self.misc or '_'
        ])
