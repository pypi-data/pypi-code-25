# -*- coding: utf-8 -*-
from unittest import TestCase
from io import open
from Document import Document
from collections import OrderedDict


TITLE = u'title: test title'
TAGS = u'tags: test tags'
BODY = u'test body'
CONTENT = TITLE + u'\n' + TAGS + u'\n\n' + BODY
my_doc = Document('test_markdown.md')


class TestDocument(TestCase):
    def create_markdown(self):
        with open('test_markdown.md', 'w+', encoding='utf-8') as f:
            f.write(CONTENT)

    def test_get_content(self):
        self.create_markdown()
        my_doc.get_content()
        assert my_doc.content in CONTENT

    def test_split_content(self):
        my_doc.split_content()
        assert BODY in my_doc.body
        assert TITLE in my_doc.meta
        assert TAGS in my_doc.meta

    def test_build_request(self):
        my_doc.process_markdown()
        test_dict = OrderedDict()
        test_dict[u'title'] = u'test title'
        test_dict[u'tags'] = u'test tags'
        test_dict[u'body'] = u'test body'
        test_dict[u'url'] = 'test_markdown'
        self.assertDictEqual(test_dict, my_doc.my_dict)
