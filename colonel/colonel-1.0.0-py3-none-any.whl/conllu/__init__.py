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

"""This package provides modules to process *CoNLL-U* formatted string,
providing a lexical analyzer (see :mod:`.lexer`) and a parser (see
:mod:`.parser`) to transform the raw string input into related
:class:`.Sentence` objects.

Lexer and parser classes are implemented taking advantage of the *PLY
(Python Lex-Yacc)* library; you can learn more from the
`PLY documentation <http://www.dabeaz.com/ply>`_ and from the
`Lex & Yacc Page <http://dinosaur.compilertools.net/>`_.
"""
