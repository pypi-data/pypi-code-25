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

"""Module providing the :class:`.Sentence` class."""

from typing import Optional, List, Iterator, Union
from colonel.base_sentence_element import BaseSentenceElement
from colonel.word import Word
from colonel.emptynode import EmptyNode
from colonel.multiword import Multiword

__all__ = ['Sentence']


class Sentence:
    """Representation of a *sentence*.

    This class is modeled starting from the *CoNLL-U Format* specification,
    which states that *sentences consist of one or more word lines*. Each
    *word line* contains a series of fields, first of all an *ID*, the
    value of which determines the *kind* of the whole line: a *single word*,
    a *(multiword) token* or an *empty node*.

    Analogously, here a :class:`Sentence` mostly consists of an ordered list of
    :attr:`elements`, which can be object of any
    :class:`.BaseSentenceElement`'s subclass, commonly a :class:`.Word`, a
    :class:`.Multiword` or an :class:`.EmptyNode`.

    Since the *CoNLL-U* format allows the presence of comment lines before a
    sentence, the :attr:`comments` attribute is made available here as a simple
    list of strings.
    """

    __slots__ = ('elements', 'comments')

    def __init__(
            self,
            elements: Optional[List[BaseSentenceElement]] = None,
            comments: Optional[List[str]] = None
    ) -> None:

        #: Ordered list of words, tokens and nodes which form the sentence.
        #:
        #: Usually this list can be freely and directly manipulated, since the
        #: methods of the class always recompute their returned value
        #: accordingly; just pay particular attention performing changes while
        #: in the context of iterations (see for example :meth:`words` and
        #: :meth:`raw_tokens` methods).
        self.elements: List[BaseSentenceElement] = \
            [] if elements is None else elements

        #: Miscellaneous comments related to the sentence.
        #:
        #: For the time being, in the context of this project no particular
        #: meaning is given to the values of this attribute, however the
        #: following guidelines *should* be followed in order to facilitate
        #: possible future usages and processing:
        #:
        #: - the presence of the leading ``#`` character (which denotes the
        #:   start of a comment line in *CoNLL-U* format) is discouraged, in
        #:   order to keep comments more format-independent;
        #: - each comment should be always stripped from leading/trailing
        #:   spaces or newline characters.
        self.comments: List[str] = [] if comments is None else comments

    def words(self) -> Iterator[Word]:
        """Extracts the sequence of words.

        Iterates through :attr:`elements` and yields :class:`.Word` elements
        only. This can be especially handy in many dependency parsing contexts,
        where the focus mostly resides among simple words and their relations,
        ignoring the additional information carried by *empty nodes* and
        *(multiword) tokens*.

        This method do not perform any validity check among the elements, so if
        you want to ensure valid and meaningful results, please refer to
        :meth:`is_valid`; unless you really know what you are doing, iterating
        an invalid sentence could lead to wrong or incoherent results or
        unexpected behaviours.
        """
        for element in self.elements:
            if isinstance(element, Word):
                yield element

    def raw_tokens(self) -> Iterator[Union[Word, Multiword]]:
        """Extracts the raw token sequence.

        Iterates through :attr:`elements` and yields the only elements which
        represent the raw sequence of tokens in the sentence. The result
        includes :class:`.Word` and :class:`.Multiword` elements,
        skipping all :class:`.Word` items which indexes are included in the
        range of a preceding :class:`.MultiWord`.

        Empty nodes are ignored.

        This method do not perform any validity check among the elements, so if
        you want to ensure valid and meaningful results, please refer to
        :meth:`is_valid`; unless you really know what you are doing, iterating
        an invalid sentence could lead to wrong or incoherent results or
        unexpected behaviours.
        """
        last_index = 0
        for element in self.elements:
            if isinstance(element, Multiword):
                yield element
                last_index = element.last_index
            elif isinstance(element, Word) and element.index > last_index:
                yield element

    def is_valid(self) -> bool:
        """Returns whether or not the sentence is valid.

        The checks implemented here are mostly based on the *CoNLL-U* format
        and on the most widely adopted common practices among NLP and
        dependency parsing contexts, yet including a minimum set of essential
        validation, so that you are free to use this as a foundation for
        other custom rules in your application.

        A sentence is considered *valid* only if **all** of the following
        conditions apply:

        - there is at least one element of type :class:`Word`;
        - every single element is valid as well - see
          :meth:`.BaseSentenceElement.is_valid` and the overriding of its
          subclasses;
        - the ordered sequence of the elements and their *ID* is valid, that
          is:
            - the sequence of :attr:`.Word.index` starts from ``1`` and
              progressively increases by 1 step;
            - there are no *index* duplicates or range overlapping;
            - the :class:`.EmptyNode` elements (if any) are correctly placed
              after the :class:`.Word` element related to their
              :attr:`.EmptyNode.main_index` (or before the first word of the
              sentence, when the *main index* is zero), and for each sequence
              of *empty nodes* their :attr:`.EmptyNode.sub_index` starts from
              ``1`` and progressively increases by 1 step;
            - the :class:`.Multiword` elements (if any) are correctly placed
              before the first :class:`.Word` included in their *index* range,
              and each range always cover existing :class:`.Word` elements in
              the sentence;
        - if one or more :attr:`.Word.head` values are set (not ``None``), each
          head must refer to the *index* of a :class:`.Word` existing within
          the sentence, or at least be equal to zero (``0``, for ``root``
          grammatical relations).
        """
        return any(self.words()) and \
            self._all_elements_are_valid() and \
            self._starts_with_valid_index() and \
            self._no_indexes_overlap() and \
            self._sequence_is_valid() and \
            self._heads_are_valid()

    def _all_elements_are_valid(self) -> bool:
        """Returns whether or not all :attr:`elements` are valid, ignoring the
        context of the whole sentence.
        """
        return all(element.is_valid() for element in self.elements)

    def _starts_with_valid_index(self) -> bool:
        """Returns whether or not the first element is a valid candidate for
        the start of a sentence, in relation to its index or indexes values.

        This is a helper method for :meth:`is_valid`; it must be called only
        if :attr:`elements` is not empty.

        The following rules apply, depending on the type of the first element
        of the sentence:
        - a :class:`Word` element is a valid candidate if its *index* is ``1``;
        - a :class:`Multiword` element is a valid candidate if its *first
          index* is ``1``;
        - an :class:`EmptyNode` element is a valid candidate if its *main
          index* is `0`.
        """
        element = self.elements[0]
        return (isinstance(element, Word) and element.index == 1) or \
            (isinstance(element, Multiword) and element.first_index == 1) or \
            (isinstance(element, EmptyNode) and element.main_index == 0)

    def _no_indexes_overlap(self):
        """Returns whether or not there are overlaps among the *index* ranges
        of :class:`.Multiword` elements (if any).

        This is a helper method for :meth:`is_valid`; it must be called only
        if all the of :attr:`elements` are valid (evaluated separately invoking
        :meth:`_all_elements_are_valid`).
        """
        ranges = set()

        for element in self.elements:
            if isinstance(element, Multiword):
                new_range = range(element.first_index, element.last_index + 1)
                range_set = set(new_range)
                if any(range_set.intersection(r) for r in ranges):
                    return False
                ranges.add(new_range)

        return True

    def _sequence_is_valid(
            self,
            position: int = 0,
            index: int = 0,
            sub_index: int = 0
    ) -> bool:
        """Returns whether or not a valid sequence of indexes is respected
        among all elements of the sentence.

        This is a helper method for :meth:`is_valid`; it must be called only
        if all the of :attr:`elements` are valid (evaluated separately invoking
        :meth:`_all_elements_are_valid`) and there are no indexes overlaps
        (see :meth:`_no_indexes_overlap`).

        For more details, refer to the documentation of :meth:`is_valid`.
        """

        if position >= len(self.elements):
            return True

        elem = self.elements[position]

        if isinstance(elem, Word):
            return elem.index == index + 1 and \
                   self._sequence_is_valid(position + 1, elem.index)

        elif isinstance(elem, Multiword):
            return elem.first_index == index + 1 and \
                   self._has_word_with_index(elem.last_index) and \
                   self._sequence_is_valid(position + 1, index)

        elif isinstance(elem, EmptyNode):
            return elem.main_index == index and \
                   elem.sub_index == sub_index + 1 and \
                   self._sequence_is_valid(position + 1, index, elem.sub_index)

        return True

    def _heads_are_valid(self) -> bool:
        """Returns whether or not the *head* values of the element are valid in
        the context of the sentence.

        This is a helper method for :meth:`is_valid`; it must be called only
        if all the of :attr:`elements` are valid (evaluated separately invoking
        :meth:`_all_elements_are_valid`) and the elements sequence is valid
        (see :meth:`_sequence_is_valid`).

        A head is considered valid only if its value is either not set
        (``None``), equals to zero (``0``, for ``root``grammatical relations),
        or less than or equal to the *index* of the last :class:`.Word` within
        the sentence.
        """
        words = list(self.words())
        last_index = words[-1].index
        return all(0 <= (word.head or 0) <= last_index for word in words)

    def _has_word_with_index(self, index: int) -> bool:
        """Returns whether or not :meth:`elements` contains a :class:`.Word`
        element with the given *index*.
        """
        return any(word.index == index for word in self.words())

    def to_conllu(self) -> str:
        """Returns a *CoNLL-U* formatted representation of the sentence.

        No validity check is performed on the sentence and its element;
        elements and values not compatible with *CoNLL-U* format could lead to
        an incorrect output value or raising of exceptions.
        """
        comments = ''.join(f'# {c}\n' for c in self.comments or [])
        word_lines = ''.join(f'{e.to_conllu()}\n' for e in self.elements)
        return f'{comments}{word_lines}\n'
