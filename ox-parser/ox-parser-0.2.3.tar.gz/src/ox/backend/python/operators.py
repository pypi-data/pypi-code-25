import enum


class Base(enum.Enum):
    def __repr__(self):
        return 'Op.' + self.name


class Op(Base):
    """
    Represent an operator
    """
    # By inverse order of precedence

    # Tests
    # We omit the ternary if statement (x if cond else y), which has the lowest
    # precedence, and the boolean negation (not x), which has the highest
    # precedence of short-circuit operators
    OR_ = 'or'
    AND_ = 'and'

    # Comparisons
    EQ = '=='
    NE = '!='
    GT = '>'
    GE = '>='
    LT = '<'
    LE = '<='
    IS = 'is'
    IS_NOT = 'is not'
    IN = 'in'
    NOT_IN = 'not in'

    # Bitwise
    OR = '|'
    XOR = '^'
    AND = '&'
    RSHIFT = '>>'
    LSHIFT = '<<'

    # Arithmetic
    # (Unary ops have a precedence between exponentiation and multiplication)
    ADD = '+'
    SUB = '-'
    MUL = '*'
    TRUEDIV = '/'
    MATMUL = '@'
    MOD = '%'
    FLOORDIV = '//'
    POW = '**'


class Unary(Base):
    """
    Unary operators.
    """

    POS = '+'
    NEG = '-'
    NOT = '~'


class Inplace(Base):
    """
    Inplace operators.
    """

    IOR = '|='
    IXOR = '^='
    IAND = '&='
    IRSHIFT = '>>='
    ILSHIFT = '<<='
    IADD = '+='
    ISUB = '-='
    IMUL = '*='
    ITRUEDIV = '/='
    IMATMUL = '@='
    IMOD = '%='
    IFLOORDIV = '//='
    IPOW = '**='


PRECEDENCE = {
    Op.OR_: 1,
    Op.AND_: 2,

    # Comparisons
    Op.EQ: 3, Op.NE: 3, Op.GT: 3, Op.GE: 3, Op.LT: 3, Op.LE: 3, Op.IS: 3,
    Op.IS_NOT: 3, Op.IN: 3, Op.NOT_IN: 3,

    # Bitwise
    Op.OR: 4,
    Op.XOR: 5,
    Op.AND: 6,
    Op.RSHIFT: 7, Op.LSHIFT: 7,

    # Plus ops
    Op.ADD: 8, Op.SUB: 8,

    # Mul ops
    Op.MUL: 9, Op.TRUEDIV: 9, Op.MATMUL: 9, Op.MOD: 9, Op.FLOORDIV: 9,

    # Power
    Op.POW: 10,
}

RIGHT_ASSOCIATIVE = {}

BINARY_OPERATORS = {k.value: k for k in Op.__members__.values()}
UNARY_OPERATORS = {k.value: k for k in Unary.__members__.values()}
INPLACE_OPERATORS = {k.value: k for k in Inplace.__members__.values()}
