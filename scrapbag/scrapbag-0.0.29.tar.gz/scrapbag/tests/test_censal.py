# -*- coding: utf-8 -*-
"""
Test Scrapbag files file
"""
import unittest
import mock

from scrapbag.censal import IneCensal


class UtilsFilesTestCase(unittest.TestCase):

    def setUp(self):
        self.ine_censal = IneCensal()

    def test_get_codigo_censal(self):

        self.assertEqual(len(self.ine_censal.index_localidades), 8228)

        self.assertEqual(self.ine_censal.get_codigo_censal('madrid'), '28079')
        self.assertEqual(self.ine_censal.get_codigo_censal(['madrid', 'falsi_provincia']), '28079')

        self.assertEqual(self.ine_censal.get_codigo_censal('castejon'), None)
        self.assertEqual(self.ine_censal.get_codigo_censal(['castejon', 'navarra']), '31070')
        self.assertEqual(self.ine_censal.get_codigo_censal(['castejon', 'cuenca']), '16067')
        self.assertEqual(self.ine_censal.get_codigo_censal(['castejon', 'cu']), '16067')
        self.assertEqual(self.ine_censal.get_codigo_censal(['caste', 'cu']), None)

        self.assertEqual(self.ine_censal.get_codigo_censal(['burriana']), '12032')
        self.assertEqual(self.ine_censal.get_codigo_censal(['chilches']), '12053')

        self.assertEqual(self.ine_censal.get_codigo_censal(['Elche/Elx']), '03065')

        self.assertEqual(self.ine_censal.get_codigo_censal(['Elche/Elx']), '03065')
