from django.test import TestCase

from django_html_assertions.mixins import HTMLContainsMixin


TEST_HTML = """
<html>
    <body>
        <p class="odd">Item 1</p>
        <p class="even">Item 2</p>
        <p class="odd">Item 3</p>
    </body>
</html>
"""


class HTMLContainsMixinTestCase(HTMLContainsMixin, TestCase):
    """
    Tests the test class mixin
    """
    def test_assert_html_tag_contains_valid(self):
        """
        The method should not raise an exception
        """
        self.assertHTMLTagContains(
            TEST_HTML,
            'Item 1',
            'p'
        )

    def test_assert_html_tag_contains_valid_with_class(self):
        """
        The method should not raise an exception
        """
        self.assertHTMLTagContains(
            TEST_HTML,
            'Item 1',
            'p',
            tag_class='odd'
        )

    def test_assert_html_tag_contains_invalid(self):
        """
        The method should raise an exception
        """
        with self.assertRaises(AssertionError):
            self.assertHTMLTagContains(
                TEST_HTML,
                'Item 10',
                'p'
            )

    def test_assert_html_tag_contains_invalid_with_class(self):
        """
        The method should not raise an exception
        """
        with self.assertRaises(AssertionError):
            self.assertHTMLTagContains(
                TEST_HTML,
                'Item 1',
                'p',
                tag_class='even'
            )

    def test_assert_html_tag_not_contains_valid(self):
        """
        The method should not raise an exception
        """
        self.assertHTMLTagNotContains(
            TEST_HTML,
            'Item 10',
            'p'
        )

    def test_assert_html_tag_not_contains_valid_with_class(self):
        """
        The method should not raise an exception
        """
        self.assertHTMLTagNotContains(
            TEST_HTML,
            'Item 1',
            'p',
            tag_class='even'
        )

    def test_assert_html_tag_not_contains_invalid(self):
        """
        The method should raise an exception
        """
        with self.assertRaises(AssertionError):
            self.assertHTMLTagNotContains(
                TEST_HTML,
                'Item 1',
                'p'
            )

    def test_assert_html_tag_not_contains_invalid_with_class(self):
        """
        The method should not raise an exception
        """
        with self.assertRaises(AssertionError):
            self.assertHTMLTagNotContains(
                TEST_HTML,
                'Item 1',
                'p',
                tag_class='odd'
            )
