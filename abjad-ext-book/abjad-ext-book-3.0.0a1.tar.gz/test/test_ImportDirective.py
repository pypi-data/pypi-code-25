import abjadext.book
import textwrap
from uqbar.strings import normalize


def test_1():
    handler = abjadext.book.SphinxDocumentHandler
    source = textwrap.dedent('''
    ..  import:: abjad.tools.topleveltools.attach
    ''')
    document = handler.parse_rst(source)
    result = normalize(document.pformat())
    expected = normalize(
        r'''
        <document source="test">
            <abjad_import_block path="abjad.tools.topleveltools.attach">
        ''')
    assert result == expected


def test_2():
    handler = abjadext.book.SphinxDocumentHandler
    source = textwrap.dedent('''
    ..  import:: abjad.tools.topleveltools.attach
        :hide:
    ''')
    document = handler.parse_rst(source)
    result = normalize(document.pformat())
    expected = normalize(
        r'''
        <document source="test">
            <abjad_import_block hide="True" path="abjad.tools.topleveltools.attach">
        ''')
    assert result == expected
