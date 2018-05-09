# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.tiles.advancedstatic.testing import COLLECTIVE_TILES_ADVANCEDSTATIC_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.tiles.advancedstatic is properly installed."""

    layer = COLLECTIVE_TILES_ADVANCEDSTATIC_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.tiles.advancedstatic is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.tiles.advancedstatic'))

    def test_browserlayer(self):
        """Test that ICollectiveTilesAdvancedstaticLayer is registered."""
        from collective.tiles.advancedstatic.interfaces import (
            ICollectiveTilesAdvancedstaticLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveTilesAdvancedstaticLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_TILES_ADVANCEDSTATIC_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.tiles.advancedstatic'])

    def test_product_uninstalled(self):
        """Test if collective.tiles.advancedstatic is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.tiles.advancedstatic'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveTilesAdvancedstaticLayer is removed."""
        from collective.tiles.advancedstatic.interfaces import ICollectiveTilesAdvancedstaticLayer
        from plone.browserlayer import utils
        self.assertNotIn(ICollectiveTilesAdvancedstaticLayer, utils.registered_layers())
