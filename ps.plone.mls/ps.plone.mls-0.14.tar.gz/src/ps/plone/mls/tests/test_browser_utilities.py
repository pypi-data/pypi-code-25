# -*- coding: utf-8 -*-
"""Test utilities from ps.plone.mls.browser.utilities."""

from plone import api
from ps.plone.mls.testing import INTEGRATION_TESTING


try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestUtilitiesView(unittest.TestCase):
    """Validate the utility methods."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        self.view = self.portal.restrictedTraverse('@@psplonemls-utils')

    def test_smart_truncate(self):
        """Validate the 'smart_truncate' method."""
        TEXT = (
            u'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
            u'Mauris suscipit orci sed sollicitudin convallis. Vestibulum '
            u'fringilla pretium velit, et elementum sapien. Pellentesque '
            u'habitant morbi tristique senectus et netus et malesuada fames '
            u'ac turpis egestas. Morbi neque quam, volutpat sed nulla non, '
            u'placerat volutpat purus. Etiam vitae nibh eget ipsum tincidunt '
            u'cursus rhoncus fermentum urna. Aliquam in ultrices magna. '
            u'Pellentesque habitant morbi tristique senectus et netus et '
            u'malesuada fames ac turpis egestas. Cras mollis lorem nibh, in '
            u'pharetra lorem tincidunt eget. Etiam ultrices vehicula tortor '
            u'ut porta. Quisque commodo ex non dapibus tincidunt.'
        )

        truncated = self.view.smart_truncate(None)
        self.assertIsNone(truncated)

        truncated = self.view.smart_truncate(TEXT)
        self.assertEqual(len(truncated), 654)

        api.portal.set_registry_record(
            name='plone.mls.listing.interfaces.IMLSUISettings.truncate_texts',
            value=True,
        )

        truncated = self.view.smart_truncate(TEXT)
        self.assertEqual(len(truncated), 319)

        self.assertEqual(
            truncated,
            u'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
            u'Mauris suscipit orci sed sollicitudin convallis. Vestibulum '
            u'fringilla pretium velit, et elementum sapien. Pellentesque '
            u'habitant morbi tristique senectus et netus et malesuada fames '
            u'ac turpis egestas. Morbi neque quam, volutpat sed nulla non, '
            u'placerat volutpat...',
        )

        api.portal.set_registry_record(
            name='plone.mls.listing.interfaces.IMLSUISettings.truncate_length',
            value=15,
        )

        truncated = self.view.smart_truncate(TEXT)
        self.assertEqual(len(truncated), 14)

        self.assertEqual(
            truncated,
            u'Lorem ipsum...',
        )
