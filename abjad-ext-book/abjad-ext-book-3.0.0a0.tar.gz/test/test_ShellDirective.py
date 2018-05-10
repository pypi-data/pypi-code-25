import abjadext.book
import textwrap
from uqbar.strings import normalize


def test_1():
    handler = abjadext.book.SphinxDocumentHandler
    source = textwrap.dedent('''
    ..  shell::

        echo "foo"
    ''')
    document = handler.parse_rst(source)
    result = normalize(document.pformat())
    expected = normalize(
        r'''
        <document source="test">
            <literal_block language="console" xml:space="preserve">
                abjad$ echo "foo"
                foo
        ''')
    assert result == expected
