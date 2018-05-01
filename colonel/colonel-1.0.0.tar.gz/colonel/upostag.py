
"""Module providing the :class:`.UposTag` enumeration."""

from enum import Enum, auto

__all__ = ['UposTag']


class UposTag(Enum):
    """Enumeration of *Universal POS tags*.

    These tags mark the core part-of-speech categories according to the
    *Universal Dependencies* framework.

    See also the ``UPOS`` field in the *CoNLL-U* format.

    **Note:** always refer to the name of each member; values are
    automatically generated and thus **MUST** be considered opaque.
    """

    #: adjective
    ADJ = auto()

    #: adposition
    ADP = auto()

    #: adverb
    ADV = auto()

    #: auxiliary
    AUX = auto()

    #: coordinating conjunction
    CCONJ = auto()

    #: determiner
    DET = auto()

    #: interjection
    INTJ = auto()

    #: noun
    NOUN = auto()

    #: numeral
    NUM = auto()

    #: particle
    PART = auto()

    #: pronoun
    PRON = auto()

    #: proper noun
    PROPN = auto()

    #: punctuation
    PUNCT = auto()

    #: subordinating conjunction
    SCONJ = auto()

    #: symbol
    SYM = auto()

    #: verb
    VERB = auto()

    #: other
    X = auto()
