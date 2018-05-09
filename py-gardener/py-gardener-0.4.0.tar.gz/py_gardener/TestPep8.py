import pycodestyle
from py_gardener.InternalTestBase import InternalTestBase


class TestPep8(InternalTestBase):
    """ Test that we conform to PEP8. """

    def test_pep8(self):
        pep8style = pycodestyle.StyleGuide(quiet=False)
        result = pep8style.check_files(self.list_project_files())
        assert result.total_errors == 0, "Found pep8 problems"
