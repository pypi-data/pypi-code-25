# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from jazkarta.abtesttile.testing import JAZKARTA_ABTESTTILE_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that jazkarta.abtesttile is properly installed."""

    layer = JAZKARTA_ABTESTTILE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if jazkarta.abtesttile is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'jazkarta.abtesttile'))

    def test_browserlayer(self):
        """Test that IJazkartaAbtesttileLayer is registered."""
        from jazkarta.abtesttile.interfaces import (
            IJazkartaAbtesttileLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IJazkartaAbtesttileLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = JAZKARTA_ABTESTTILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['jazkarta.abtesttile'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if jazkarta.abtesttile is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'jazkarta.abtesttile'))

    def test_browserlayer_removed(self):
        """Test that IJazkartaAbtesttileLayer is removed."""
        from jazkarta.abtesttile.interfaces import \
            IJazkartaAbtesttileLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IJazkartaAbtesttileLayer,
            utils.registered_layers())
