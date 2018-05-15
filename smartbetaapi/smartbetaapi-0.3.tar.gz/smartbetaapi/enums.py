from enum import Enum, unique


@unique
class AttributeOperator(Enum):
    """List of operators applicable in the AttributeFilter class

    """
    IN = 0  #:
    NOT_IN = 1  #:

@unique
class MeasureOperator(Enum):
    """List of operators applicable in the MeasureFilter class

    """
    EQ = 0  #:
    LT = 1  #:
    GT = 2  #:
    BETWEEN = 3  #:
    LT_EQ = 4  #:
    GT_EQ = 5  #:
    NOT_BETWEEN = 6  #:


@unique
class JoinType(Enum):
    """Specifies how UniverseContext filters can be joined together.

    """
    AND = 0  #:
    OR = 1  #:


@unique
class QueryItemType(Enum):
    UNKNOWN = 0
    IDENTIFIER = 1
    ATTRIBUTE = 2
    MEASURE = 3