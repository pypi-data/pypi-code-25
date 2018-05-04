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

"""Module providing the :class:`.Multiword` class."""

from typing import Optional
from colonel.base_sentence_element import BaseSentenceElement

__all__ = ['Multiword']


class Multiword(BaseSentenceElement):
    """Representation of a *Multiword Token* sentence element"""

    __slots__ = ('first_index', 'last_index')

    def __init__(
            self,
            first_index: Optional[int] = None,
            last_index: Optional[int] = None,
            **kwargs
    ) -> None:
        super(Multiword, self).__init__(**kwargs)

        #: The first word index (inclusive) covered by the multiword token.
        #:
        #: This usually corresponds to the value of the :attr:`.Word.index`
        #: of the first :class:`.Word` which is part of this multiword token.
        #:
        #: It is compatible with *CoNLL-U* ``ID`` field, which in case of a
        #: multiword token is a range of integer numbers, where first and last
        #: bound indexes are separated by a dash (``-``): the first index here
        #: corresponds to the value at left.
        self.first_index: Optional[int] = first_index

        #: The last word index (inclusive) covered by the multiword token.
        #:
        #: This usually corresponds to the value of the :attr:`.Word.index`
        #: of the last :class:`.Word` which is part of this multiword token.
        #:
        #: It is compatible with *CoNLL-U* ``ID`` field, which in case of a
        #: multiword token is a range of integer numbers, where first and last
        #: bound indexes are separated by a dash (``-``): the first index here
        #: corresponds to the value at right.
        self.last_index: Optional[int] = last_index

    def is_valid(self) -> bool:
        """Returns whether or not the object can be considered valid,
        however ignoring the context of the sentence in which the word
        itself is possibly inserted.

        In compliance with the _CoNLL-U_ format, an instance of type
        :class:`.Multiword` is considered valid only when :attr:`first_index`
        is set to a value greater than zero (``0``) **and**
        :attr:`last_index` is set to a value greater than :attr:`first_index`.
        """
        return super(Multiword, self).is_valid() and \
            self.first_index is not None and \
            self.last_index is not None and \
            0 < self.first_index < self.last_index

    def to_conllu(self) -> str:
        """Returns a *CoNLL-U* formatted representation of the element.

        No validity check is performed on the attributes; values not compatible
        with *CoNLL-U* format could lead to an incorrect output value or
        raising of exceptions.
        """
        return '\t'.join([
            f'{self.first_index}-{self.last_index}',
            self.form or '_',
            '_',  # Lemma
            '_',  # UPOS
            '_',  # XPOS
            '_',  # Feats
            '_',  # Head
            '_',  # DepRel
            '_',  # Deps
            self.misc or '_'
        ])
