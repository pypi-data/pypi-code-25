from alchemist_stack.context import UnsupportedDriverException, UnsupportedDialectException,\
    set_connection_string_settings, create_context, __settings__
from alchemist_stack.context.context import Context
from alchemist_stack.utils import dict_diff

from copy import deepcopy
from sqlalchemy.engine import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
import unittest

__author__ = 'H.D. "Chip" McCullough IV'

class TestContextCreation(unittest.TestCase):
    def setUp(self):
        self.connection_variables = {
            'drivername': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'username': 'python',
            'password': 'password',
            'database': 'data'
        }
        self.settings_copy = deepcopy(__settings__)
        self.fake_dialect = 'lionfish'
        self.fake_driver = 'postgresql+pufferfish'
        self.fake_dialect_real_driver = 'triggerfish+psycopg2'

    def test_set_connection_string_settings(self):
        set_connection_string_settings(**self.connection_variables)
        self.assertEqual(self.connection_variables, __settings__,
                         msg='The following values were different than expected:\n{diff}'
                            .format(diff=dict_diff(self.connection_variables, __settings__)))

    def test_bad_dialect_in_settings(self):
        connection_variables_copy: dict = deepcopy(self.connection_variables)
        connection_variables_copy.update({ 'drivername': self.fake_dialect })
        with self.assertRaises(UnsupportedDialectException,
                               msg='The function did not raise the correct Exception') as cm:
            set_connection_string_settings(**connection_variables_copy)

        exception: UnsupportedDialectException = cm.exception
        self.assertEqual(self.fake_dialect, exception.dialect,
                         msg='The dialect names do not match.')
        self.assertIsNone(exception.driver,
                          msg='The value of the driver was {driver}, with type {type}'
                            .format(driver=exception.driver,
                                    type=type(exception.driver)))

    def test_bad_driver_in_settings(self):
        (dialect, driver) = self.fake_driver.split('+')
        connection_variables_copy: dict = deepcopy(self.connection_variables)
        connection_variables_copy.update({ 'drivername': self.fake_driver })
        with self.assertRaises(UnsupportedDriverException,
                               msg='The function did not raise the correct Exception') as cm:
            set_connection_string_settings(**connection_variables_copy)

        exception: UnsupportedDriverException = cm.exception
        self.assertEqual(dialect, exception.dialect,
                         msg='The dialect names do not match.')
        self.assertIsNotNone(exception.driver,
                             msg='The Exception\'s `driver` value is None.')
        self.assertEqual(driver, exception.driver,
                          msg='The driver names do not match')

    def test_bad_dialect_real_driver_in_settings(self):
        (dialect, driver) = self.fake_dialect_real_driver.split('+')
        connection_variables_copy: dict = deepcopy(self.connection_variables)
        connection_variables_copy.update({ 'drivername': self.fake_dialect_real_driver })
        with self.assertRaises(UnsupportedDialectException,
                               msg='The function did not raise the correct Exception') as cm:
            set_connection_string_settings(**connection_variables_copy)

        exception: UnsupportedDialectException = cm.exception
        self.assertEqual(dialect, exception.dialect,
                         msg='The dialect names do not match.')
        self.assertIsNotNone(exception.driver,
                             msg='The Exception\'s `driver` value is None.')
        self.assertEqual(driver, exception.driver,
                         msg='The driver names do not match')

    def test_successful_create_context(self):
        set_connection_string_settings(**self.connection_variables)
        ctxt: Context = create_context()
        engine: Engine = create_engine(URL(**self.connection_variables))

        self.assertEqual(str(engine), str(ctxt),
                         msg='The generated connection strings for the engine do not match.')

    def tearDown(self):
        del self.connection_variables
        del self.settings_copy
        del self.fake_dialect
        del self.fake_driver
        del self.fake_dialect_real_driver


class TestContextClass(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()