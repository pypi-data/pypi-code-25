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

"""This package provides methods and modules to process the *CoNLL-U* format.

In most situations it's sufficient to make use of :func:`parse` and
:func:`to_conllu` functions, without caring too much about the implementation
under the hood.

In more detail, this package provides a lexical analyzer (see :mod:`.lexer`)
and a parser (see :mod:`.parser`) to transform the raw string input into
related :class:`.Sentence` objects.

Lexer and parser classes are implemented taking advantage of the *PLY
(Python Lex-Yacc)* library; you can learn more from the
`PLY documentation <http://www.dabeaz.com/ply>`_ and from the
`Lex & Yacc Page <http://dinosaur.compilertools.net/>`_.
"""

from typing import List
from colonel.sentence import Sentence
from colonel.conllu.parser import ConlluParserBuilder


def parse(content: str) -> List[Sentence]:
    """Parses a *CoNLL-U* string content, returning a list of sentences.

    :raise lexer.LexerError: (any specific subclass) in case of invalid input
        breaking the rules of the *CoNLL-U* lexer
    :raise parser.ParserError: (any specific subclass) in case of invalid input
        breaking the rules of the *CoNLL-U* parser

    :param content: *CoNLL-U* formatted string to be parsed
    :return: list of parsed :class:`.Sentence` items
    """
    return ConlluParserBuilder.build().parse(content)


def to_conllu(sentences: List[Sentence]) -> str:
    """Serializes a list of sentences to a formatted *CoNLL-U* string.

    This method simply concatenates the output of :meth:`.Sentence.to_conllu`
    for each given sentence and do not perform any validity check;
    sentences and elements not compatible with *CoNLL-U* format could lead to
    an incorrect output value or raising of exceptions.

    :param sentences: list of :class:`.Sentence` items
    :return: a *CoNLL-U* formatted representation of the sentences
    """
    return ''.join(sentence.to_conllu() for sentence in sentences)
