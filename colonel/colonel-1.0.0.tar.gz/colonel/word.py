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

"""Module providing the :class:`.Word` class."""

from typing import Optional
from colonel.base_rich_sentence_element import BaseRichSentenceElement

__all__ = ['Word']


class Word(BaseRichSentenceElement):
    """Representation of a *Word* sentence element"""

    __slots__ = ('index', 'head', 'deprel')

    def __init__(
            self,
            index: Optional[int] = None,
            head: Optional[int] = None,
            deprel: Optional[str] = None,
            **kwargs
    ) -> None:
        super(Word, self).__init__(**kwargs)

        #: Word index.
        #:
        #: It is compatible with *CoNLL-U* ``ID`` field.
        #:
        #: The term *index* has been preferred over the more conventional *ID*,
        #: mostly for the purpose of preventing confusion, especially with
        #: Python's :func:`id` built-in function (which returns the
        #: *"identity"* of an object).
        self.index: Optional[int] = index

        #: Head of the current word, which is usually a value of another
        #: Word's :attr:`index` or zero (``0``, for ``root`` grammatical
        #: relations).
        #:
        #: It is compatible with *CoNLL-U* ``HEAD`` field.
        self.head: Optional[int] = head

        #: *Universal dependency relation* to the :attr:`head` or a defined
        #: language-specific subtype of one.
        #:
        #: It is compatible with *CoNLL-U* ``DEPREL`` field.
        self.deprel: Optional[str] = deprel

    def is_valid(self) -> bool:
        """Returns whether or not the object can be considered valid,
        however ignoring the context of the sentence in which the word
        itself is possibly inserted.

        In compliance with the *CoNLL-U* format, an instance of type
        :class:`.Word` is considered valid only when :attr:`index` is set to a
        value greater than zero (``0``).
        """
        return super(Word, self).is_valid() and \
            self.index is not None and self.index > 0

    def to_conllu(self) -> str:
        """Returns a *CoNLL-U* formatted representation of the element.

        No validity check is performed on the attributes; values not compatible
        with *CoNLL-U* format could lead to an incorrect output value or
        raising of exceptions.
        """
        return '\t'.join([
            str(self.index),
            self.form or '_',
            self.lemma or '_',
            self.upos.name if self.upos else '_',
            self.xpos or '_',
            self._feats_to_conllu(),
            str(self.head) if self.head is not None else '_',
            self.deprel or '_',
            self._deps_to_conllu(),
            self.misc or '_'
        ])
