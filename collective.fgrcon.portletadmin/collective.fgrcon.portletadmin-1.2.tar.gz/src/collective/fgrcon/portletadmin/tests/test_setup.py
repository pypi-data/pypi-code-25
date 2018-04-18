# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from collective.fgrcon.portletadmin.testing import COLLECTIVE_FGRCON_PORTLETADMIN_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.fgrcon.portletadmin is properly installed."""

    layer = COLLECTIVE_FGRCON_PORTLETADMIN_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.fgrcon.portletadmin is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.fgrcon.portletadmin'))

    def test_browserlayer(self):
        """Test that ICollectiveFgrconPortletadminLayer is registered."""
        from collective.fgrcon.portletadmin.interfaces import (
            ICollectiveFgrconPortletadminLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveFgrconPortletadminLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_FGRCON_PORTLETADMIN_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.fgrcon.portletadmin'])

    def test_product_uninstalled(self):
        """Test if collective.fgrcon.portletadmin is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.fgrcon.portletadmin'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveFgrconPortletadminLayer is removed."""
        from collective.fgrcon.portletadmin.interfaces import \
            ICollectiveFgrconPortletadminLayer
        from plone.browserlayer import utils
        self.assertNotIn(ICollectiveFgrconPortletadminLayer, utils.registered_layers())
