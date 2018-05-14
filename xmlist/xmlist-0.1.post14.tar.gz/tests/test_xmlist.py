import unittest

import xmlist

import sys

if sys.version_info[0] == 3:
    long = int
if sys.version_info[0] == 2:
    unittest.TestCase.assertEqual = unittest.TestCase.assertEquals

class TestSerializeXml(unittest.TestCase):
    def setUp(self):
        xmlist.MODE = xmlist.MODE_XML

    def test_empty_elem(self):
        doc = xmlist.serialize(['foo'])
        self.assertEqual(doc, '<foo/>')

    def test_sub_elem(self):
        doc = xmlist.serialize(['html', ['head'], ['body']])
        self.assertEqual(doc, '<html><head/><body/></html>')

    def test_attr(self):
        doc = xmlist.serialize(['a', ('b', 'c')])
        self.assertEqual(doc, '<a b="c"/>')

    def test_text(self):
        doc = xmlist.serialize(['a', 'foo'])
        self.assertEqual(doc, '<a>foo</a>')

    def test_int_long(self):
        doc = xmlist.serialize(['doc', ['int', 42], ['long', long(42)]])
        self.assertEqual(doc, '<doc><int>42</int><long>42</long></doc>')

    def test_unicode(self):
        doc = xmlist.serialize(['doc', u'foo'])
        self.assertEqual(doc, '<doc>foo</doc>')

    def test_xml_br(self):
        doc = xmlist.serialize(['body', ['br']])
        self.assertEqual(doc, '<body><br/></body>')

class TestSerializeHtml(unittest.TestCase):
    def setUp(self):
        xmlist.MODE = xmlist.MODE_HTML

    def test_html_br(self):
        doc = xmlist.serialize(['body', ['br']])
        self.assertEqual(doc, '<body><br></body>')

    def test_html_nonempty_br(self):
        with self.assertRaises(ValueError) as ex:
            xmlist.serialize(['br', ['p']])
        self.assertEqual(ex.exception.args[0], 'br not empty')

class TestSerializeFuckedUp(unittest.TestCase):
    def setUp(self):
        xmlist.MODE = 'whatever'

    def test_anything(self):
        with self.assertRaises(ValueError) as ex:
            xmlist.serialize(['foo', ['bar']])
        self.assertEqual(ex.exception.args[0], 'mode whatever not recognized')
            

class TestSerializeWeirdThings(unittest.TestCase):
    def setUp(self):
        xmlist.MODE = xmlist.MODE_XML

    def test_procinc(self):
        doc = xmlist.serialize(['spam', 
            [xmlist.PROCINC, 'albatross', ('spanish_inquisition', 'unexpected')]])
        self.assertEqual(doc, '<spam><?albatross spanish_inquisition="unexpected"?></spam>')

    def test_fragment(self):
        doc = xmlist.serialize(['spam', [xmlist.FRAGMENT, ['albatross']]])
        self.assertEqual(doc, '<spam><albatross/></spam>')

    def test_comment(self):
        doc = xmlist.serialize([xmlist.COMMENT, 'albatross'])
        self.assertEqual(doc, '<!--albatross-->')

    def test_cdata(self):
        doc = xmlist.serialize([xmlist.CDATA, '<albatross/>'])
        self.assertEqual(doc, '<![CDATA[<albatross/>]]>')

    def test_doctype(self):
        doc = xmlist.serialize([xmlist.DOCTYPE, 'HTML 5'])
        self.assertEqual(doc, '<!DOCTYPE html>\n')

    def test_aah_wtf_are_you_doing(self):
        with self.assertRaises(ValueError) as ex:
            xmlist.serialize(['wtf', [13, 'albatross']])
        self.assertEqual(ex.exception.args[0], '[13, \'albatross\']')

class TestXmlistWhitespace(unittest.TestCase):
    def setUp(self):
        xmlist.MODE = xmlist.MODE_XML

    def test_elem(self):
        doc = ['foo', ['bar']]
        xmlist.insert_ws(doc)
        self.assertEqual(doc, ['foo', '\n    ', ['bar'], '\n'])

    def test_text(self):
        doc = ['spam', 'albatross']
        xmlist.insert_ws(doc)
        self.assertEqual(doc, ['spam', 'albatross'])

    def test_procinc(self):
        doc = ['foo', [xmlist.PROCINC, 'a', ('b', 'c')]]
        xmlist.insert_ws(doc)
        self.assertEqual(doc, ['foo',
            '\n    ',
            [xmlist.PROCINC, 'a', ('b', 'c')],
            '\n'])
        xml = xmlist.serialize(doc)
        self.assertEqual('\n' + xml, '''
<foo>
    <?a b="c"?>
</foo>''')

    def test_procinc_2(self):
        doc = [xmlist.PROCINC, 'foo', ('a', 'b')]
        xmlist.insert_ws(doc)
        self.assertEqual(doc, [xmlist.PROCINC, 'foo', ('a', 'b')])

    def test_fragment(self):
        doc = ['foo', 
                ['quux', 
            [xmlist.FRAGMENT, ['bar']]]]
        xmlist.insert_ws(doc)
        self.assertEqual(doc, ['foo',
            '\n    ',
            ['quux',
                '\n        ',
                [xmlist.FRAGMENT, ['bar']],
                '\n    '],
            '\n'])
        xml = xmlist.serialize(doc)
        self.assertEqual('\n' + xml, '''
<foo>
    <quux>
        <bar/>
    </quux>
</foo>''')

    def test_fragment_2(self):
        doc = [xmlist.FRAGMENT, ['spam', ['albatross'], ['albatross', ('inquisition', 'spanish')]]]
        xmlist.insert_ws(doc)
        self.assertEqual(doc, [xmlist.FRAGMENT, 
            ['spam',
                '\n    ',
                ['albatross'],
                '\n    ',
                ['albatross', ('inquisition', 'spanish')],
                '\n']])

    def test_attr(self):
        doc = ['a', ('href', 'http://j0057.nl/'), 'j0057.nl', 'test']
        xmlist.insert_ws(doc)
        self.assertEqual(doc, ['a', ('href', 'http://j0057.nl/'), '\n    ', 'j0057.nl', '\n    ', 'test', '\n'])

class TestSerializeWhitespace(unittest.TestCase):
    def setUp(self):
        xmlist.MODE = xmlist.MODE_XML

    def test_ws(self):
        doc = xmlist.serialize_ws(['spam', ['inquisition', 'spanish'], ['albatross']])
        self.assertEqual('\n' + doc, '''
<spam>
    <inquisition>spanish</inquisition>
    <albatross/>
</spam>''')

class TestUnicode(unittest.TestCase):
    def setUp(self):
        xmlist.MODE = xmlist.MODE_XML

    def test_unicode_text_node(self):
        xml = xmlist.serialize(['spam', u'\u20a0 99'])
        self.assertEqual(xml, u'<spam>\u20a0 99</spam>')

    def test_unicode_element_name(self):
        xml = xmlist.serialize([u'spam\u20a0', 'test'])
        self.assertEqual(xml, u'<spam\u20a0>test</spam\u20a0>') 

    def test_unicode_attr_name(self):
        xml = xmlist.serialize(['spam', (u'\u20a0', 'spam & albatross')])
        self.assertEqual(xml, u'<spam \u20a0="spam &amp; albatross"/>')

