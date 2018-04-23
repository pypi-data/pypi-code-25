import logging
from unittest import TestCase
import os

import pytest

import snitcher

logging.basicConfig(level="DEBUG")


class Agent:

    def __init__(self):
        self.data = 0
        self.last_scoop = None

    def notify(self, scoop=None, **kwargs):
        self.data += 1
        self.last_scoop = scoop
        self.old_value = kwargs.get('old_value', None)
        self.new_value = kwargs.get('new_value', None)


class TestScoop(TestCase):

    def test_repr(self):
        s = snitcher.Scoop()
        self.assertEqual(repr(s), 'Scoop(None)')

    def test_add(self):
        s1 = snitcher.Scoop()
        s2 = snitcher.Scoop()
        s1.s_add(s2)
        self.assertEqual(s1.next, s2)
        s3 = snitcher.Scoop()
        s1.s_add(s3)
        self.assertEqual(s2.next, s3)
        self.assertIsNone(s3.next)

    def test_iterate(self):
        s1 = snitcher.Scoop()
        nested = list(s1)
        self.assertEqual(len(nested), 1)
        s2 = snitcher.Scoop()
        s1.s_add(s2)
        s3 = snitcher.Scoop()
        s1.s_add(s3)
        nested = list(s1)
        self.assertEqual(len(nested), 3)
        self.assertListEqual(nested, [s1, s2, s3])


class TestSnitcher(TestCase):

    def test_register_agent(self):
        s = snitcher.Snitcher()
        a = Agent()
        s.s_register_agent(a)
        self.assertIn(a, s.s_agents())

    def test_unregister_agent(self):
        s = snitcher.Snitcher()
        a = Agent()
        s.s_register_agent(a)
        self.assertIn(a, s.s_agents())
        s.s_unregister_agent(a)
        self.assertNotIn(a, s.s_agents())

    def test_unregister_unregistered_agent(self):
        s = snitcher.Snitcher()
        a = Agent()
        # Unknown agents are ignored silently, but logged
        s.s_unregister_agent(a)

    def test_unregister_all(self):
        s = snitcher.Snitcher()
        a1 = Agent()
        a2 = Agent()
        s.s_register_agent(a1)
        s.s_register_agent(a2)
        self.assertIn(a1, s.s_agents())
        self.assertIn(a2, s.s_agents())
        s.s_unregister_all()
        self.assertNotIn(a1, s.s_agents())
        self.assertNotIn(a2, s.s_agents())

    def test_agent_no_notify_method(self):
        class CIAAgent:
            pass
        s = snitcher.Snitcher()
        a1 = CIAAgent()
        with pytest.raises(AttributeError):
            s.s_register_agent(a1)

    def test_register_alternate_callback(self):
        class CIAAgent:
            def __init__(self):
                self.tells = 0

            def tell(self, *args, **kwargs):
                self.tells += 1

        s = snitcher.Snitcher()
        a1 = Agent()
        a2 = CIAAgent()
        s.s_register_agent(a1)
        s.s_register_agent(a2, a2.tell)
        s.s_inform()
        self.assertEqual(a2.tells, 1)

    def test_callback_call(self):
        s = snitcher.Snitcher()
        a = Agent()
        s.s_register_agent(a)
        s.s_inform()
        self.assertEqual(a.data, 1)
        a2 = Agent()
        s.s_register_agent(a2)
        s.s_inform()
        self.assertEqual(a.data, 2)
        self.assertEqual(a2.data, 1)

    def test_callback_with_scoop(self):
        s = snitcher.Snitcher()
        a = Agent()
        s.s_register_agent(a)
        scoop = snitcher.Scoop(type='Simple')
        s.s_inform(scoop=scoop)
        self.assertEqual(scoop, a.last_scoop)

    def test_callback_with_kwargs(self):
        s = snitcher.Snitcher()
        a = Agent()
        s.s_register_agent(a)
        scoop = snitcher.Scoop(type='Simple')
        data = {'old_value': 20, 'new_value': 21}
        s.s_inform(scoop=scoop, **data)
        self.assertEqual(scoop, a.last_scoop)
        self.assertEqual(20, a.old_value)
        self.assertEqual(21, a.new_value)

    def test_callback_call_not_talking(self):
        s = snitcher.Snitcher()
        a = Agent()
        s.s_register_agent(a)
        s.s_chatty = False
        s.s_inform()
        self.assertEqual(a.data, 0)
        s.s_inform()
        self.assertEqual(a.data, 0)

    def test_callback_no_method(self):
        s = snitcher.Snitcher()
        a = Agent()
        a.fake_method = 3
        s.s_register_agent(a, a.fake_method)
        with pytest.raises(TypeError):
            s.s_inform()


