from lib.TestIncorrectBoolConditional import TestIncorrectBoolConditional
from lib.TestLineEndings import TestLineEndings
from lib.TestPep8 import TestPep8
from lib.TestPylint import TestPylint
from lib.TestStructure import TestStructure
from lib.TestVersionConsistent import TestVersionConsistent


class StaticTestBase(
    TestIncorrectBoolConditional,
    TestLineEndings,
    TestPep8,
    TestPylint,
    TestStructure,
    TestVersionConsistent
):
    pass
