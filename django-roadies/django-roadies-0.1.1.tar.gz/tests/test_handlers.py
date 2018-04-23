from __future__ import absolute_import, print_function, unicode_literals

from django.db.models.signals import post_init, post_save
from django.dispatch import Signal
from django.test import TestCase
from tests.myapp.models import Foo, test_handler
from roadies.handlers import handler, Handler

try:
    import mock
except ImportError:
    from unittest import mock


def async_action(*args):
    pass


@handler
def do_something(sender, foo, bar, **kwargs):
    """Test functional handlers."""
    async_action(foo, bar)


@handler(post_init, sender='myapp.Foo', dispatch_uid='testing')
def do_something_else(sender, instance, **kwargs):
    async_action(instance)


test_signal = Signal(providing_args=['foo', 'bar'])


class HandlerTests(TestCase):

    def test_do_something_is_handler_instance(self):
        self.assertIsInstance(do_something, Handler)

    def test_connect_no_sender(self):
        do_something.connect(test_signal, dispatch_uid='testing')
        result = do_something.disconnect(test_signal, dispatch_uid='testing')
        self.assertTrue(result)
        result = do_something.disconnect(test_signal, dispatch_uid='testing')
        self.assertFalse(result)

    def test_connect_with_sender_string(self):
        do_something.connect(
            test_signal,
            sender='myapp.Foo',
            dispatch_uid='testing'
        )
        disconnected = do_something.disconnect(
            test_signal,
            sender='myapp.Foo',
            dispatch_uid='testing'
        )
        self.assertTrue(disconnected)

        disconnected = do_something.disconnect(
            test_signal,
            sender='myapp.Foo',
            dispatch_uid='testing'
        )
        self.assertFalse(disconnected)

    def test_do_something_name(self):
        self.assertEqual(do_something.__name__, 'do_something')

    def test_do_something_module(self):
        self.assertEqual(do_something.__module__, 'tests.test_handlers')

    def test_do_something_doc(self):
        self.assertEqual(do_something.__doc__, 'Test functional handlers.')

    def test_do_something_does_something_on_signal(self):
        do_something.connect(test_signal, dispatch_uid='testing')
        with mock.patch('tests.test_handlers.async_action') as func:
            test_signal.send(None, foo=1, bar=2)
            self.assertTrue(func.called)
            func.assert_called_once_with(1, 2)

    def test_do_something_else_is_handler(self):
        self.assertIsInstance(do_something_else, Handler)

    def test_do_something_else_executed_on_post_init(self):
        with mock.patch('tests.test_handlers.async_action') as func:
            instance = Foo(bar='baz')
            self.assertTrue(func.called)
            func.assert_called_once_with(instance)

    def test_calling_the_handler_directly(self):
        with mock.patch('tests.test_handlers.async_action') as func:
            do_something(None, 'foo', 'bar')
            self.assertTrue(func.called)
            func.assert_called_once_with('foo', 'bar')

    def test_autodiscover_works(self):
        self.assertTrue(
            post_save.disconnect(test_handler, dispatch_uid='test_handler')
        )
