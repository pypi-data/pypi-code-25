from bs4 import BeautifulSoup


class HTMLContainsMixin(object):
    """A testing Mixin that adds the assertHTMLTagContains test case."""
    def _get_raw_tags(self, context, tag, tag_class):
        """Returns the raw tags from a HTML document.
        :param context: A HTML document.
        :param tag: A string of the HTML Tag to be searched.
        :param tag_class: A string of the class of a HTML Tag.
        """
        soup = BeautifulSoup(context, 'html.parser')
        if tag_class:
            return soup.find_all(tag, class_=tag_class)
        return soup.find_all(tag)

    def assertHTMLTagContains(self, context, expected, tag, tag_class=None):
        """A test case for determining if a HTML tag contains a given string.
        :param context: A HTML document.
        :param expected: The string to be found within the HTML Tag.
        :param tag: A string of the HTML Tag to be searched.
        :param tag_class: A string of the class of a HTML Tag.
        """
        tags_raw = self._get_raw_tags(context, tag, tag_class)

        if expected not in [item.string.strip() for item in tags_raw]:
            raise AssertionError(
                'Expected "{0}" not found within Tag:{1} Class:{2}\n Content:{3}'.format(
                    expected,
                    tag,
                    tag_class,
                    tags_raw,
                )
            )

    def assertHTMLTagNotContains(self, context, expected, tag, tag_class=None):
        """A test case for determining if a HTML tag does not contains a given string.
        :param context: A HTML document.
        :param expected: The string to be found within the HTML Tag.
        :param tag: A string of the HTML Tag to be searched.
        :param tag_class: A string of the class of a HTML Tag.
        """
        tags_raw = self._get_raw_tags(context, tag, tag_class)

        if expected in [item.string.strip() for item in tags_raw]:
            raise AssertionError(
                'Expected "{0}" found within Tag:{1} Class:{2}\n Content:{3}'.format(
                    expected,
                    tag,
                    tag_class,
                    tags_raw,
                )
            )
