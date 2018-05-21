import unittest

from yangsutil import ObjectUtil
from tests.app.main import TestApp


class ObjectUtilTestCase(unittest.TestCase):
    def setUp(self):
        self.MODULE_NAME = 'tests.app.main'
        self.CLASS_NAME = 'TestApp'

    def test_1_get_class(self):
        self.assertEqual(
            ObjectUtil.get_class(
                module_name=self.MODULE_NAME,
                class_name=self.CLASS_NAME
            ),
            TestApp,
            msg="class by module name, class name"
        )

    def test_2_get_class_by_path(self):
        self.assertEqual(
            ObjectUtil.get_class_by_path('%s.%s' % (self.MODULE_NAME, self.CLASS_NAME)),
            TestApp,
            msg="class by module path"
        )

    def test_3_get_empty_class_by_path(self):
        self.assertIsNone(
            ObjectUtil.get_class_by_path('tests.app.mmmm.TestApp'),
            msg='call error module'
        )

        self.assertIsNone(
            ObjectUtil.get_class_by_path('tests.app.main.Test'),
            msg='call error class'
        )
