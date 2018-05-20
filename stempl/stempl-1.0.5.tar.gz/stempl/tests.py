from unittest import TestCase
from stempl import *


class StemplTestCase(TestCase):

    def test_empty_tag(self):
        self.assertEqual('<br></br>', br())
        self.assertEqual('<br></br>', Br()())

    def test_tag_function(self):
        self.assertEqual('<h1>test</h1>', h1('test'))
        self.assertEqual('<p>test</p>', p('test'))
        self.assertEqual('<div>test</div>', div('test'))

    def test_tag_attr(self):
        self.assertEqual('<h1 style="color:#000" title="test title">test</h1>',
                         h1('test', style='color:#000', title='test title'))

    def test_keyword_named_tag_attr(self):
        self.assertEqual('<p class="c" def="d">body</p>',
                         p('body', _class='c', _def='d'))

    def test_dashed_tag_attr(self):
        self.assertEqual('<div data-toggle="dt">body</div>',
                         div('body', data_toggle='dt'))

    def test_empty_attr(self):
        self.assertEqual('<div data-visible="">body</div>',
                         div('body', data_visible=''))

    def test_tag_function_inside_tag_function(self):
        self.assertEqual('<p><h1>test</h1></p>',
                         p(h1('test')))
        self.assertEqual('<p><h1>test</h1></p>',
                         P() << h1('test'))
        self.assertEqual('<div><h1 class="cls"><i>test</i></h1></div>',
                         Div() << (H1(_class='cls') << i('test')))

    def test_tag_class(self):
        self.assertEqual('<h1>test</h1>',
                         H1()('test'))
        self.assertEqual('<h1 class="cls">test</h1>',
                         H1(_class='cls')('test'))
        self.assertEqual('<h1 class="cls">test</h1>',
                         H1()('test', _class='cls'))

    def test_tag_context(self):
        with Div() as d:
            d << p('test')
        self.assertEqual('<div><p>test</p></div>', d())

    def test_lshift_with_callable(self):
        with Div() as d:
            d << br
        self.assertEqual('<div><br></br></div>', d())
        self.assertEqual('<h1><br></br></h1>', H1() << br)

    def test_tag_context_with_attr(self):
        with Div(_class='cls', data_toggle='') as d:
            d << p('test', _class='pcls')
        self.assertEqual('<div class="cls" data-toggle="">'
                         '<p class="pcls">test</p>'
                         '</div>', d())

    def test_context_within_context(self):
        with Div() as d1:
            d1 << p('before d2')
            with Div() as d2:
                d2 << p('inside d2')
            d1 << d2()
        self.assertEqual('<div>'
                         '<p>before d2</p>'
                         '<div><p>inside d2</p></div>'
                         '</div>', d1())

    def test_doctype(self):
        self.assertEqual('<!DOCTYPE html>', doctype())
