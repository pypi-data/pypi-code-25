# -*- coding: utf-8 -*-
"""Test Control Panel for plone.mls.core."""

from plone import api
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry import Registry
from ps.plone.mls.browser.interfaces import IPloneMLSLayer
from ps.plone.mls.interfaces import IMLSBaseSettings
from ps.plone.mls.interfaces import IMLSCachingSettings
from ps.plone.mls.interfaces import IMLSContactInfoSettings
from ps.plone.mls.interfaces import IMLSUISettings
from ps.plone.mls.testing import INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestMLSBaseControlPanel(unittest.TestCase):
    """Validate base control panel is available."""
    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        alsoProvides(self.portal.REQUEST, IPloneMLSLayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = Registry()
        self.registry.registerInterface(IMLSBaseSettings)

    def test_controlpanel_view(self):
        """Validate that the configuration view is available."""
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='mls-controlpanel-base',
        )
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_protected(self):
        """Validate that the configuration view needs authentication."""
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(
            Unauthorized,
            self.portal.restrictedTraverse,
            '@@mls-controlpanel-base',
        )

    def test_mls_in_controlpanel(self):
        """Validate that there is an MLS entry in the control panel."""
        controlpanel = api.portal.get_tool(name='portal_controlpanel')
        actions = [
            a.getAction(self)['id'] for a in controlpanel.listActions()
        ]
        self.assertTrue('ps_plone_mls' in actions)


class TestMLSCachingControlPanel(unittest.TestCase):
    """Validate caching control panel is available."""
    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        alsoProvides(self.portal.REQUEST, IPloneMLSLayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = Registry()
        self.registry.registerInterface(IMLSCachingSettings)

    def test_controlpanel_view(self):
        """Validate that the configuration view is available."""
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='mls-controlpanel-caching',
        )
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_protected(self):
        """Validate that the configuration view needs authentication."""
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(
            Unauthorized,
            self.portal.restrictedTraverse,
            '@@mls-controlpanel-caching',
        )


class TestMLSContactInfoControlPanel(unittest.TestCase):
    """Validate contact info control panel is available."""
    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        alsoProvides(self.portal.REQUEST, IPloneMLSLayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = Registry()
        self.registry.registerInterface(IMLSContactInfoSettings)

    def test_controlpanel_view(self):
        """Validate that the configuration view is available."""
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='mls-controlpanel-contact-info',
        )
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_protected(self):
        """Validate that the configuration view needs authentication."""
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(
            Unauthorized,
            self.portal.restrictedTraverse,
            '@@mls-controlpanel-contact-info',
        )


class TestMLSUIControlPanel(unittest.TestCase):
    """Validate ui control panel is available."""
    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        alsoProvides(self.portal.REQUEST, IPloneMLSLayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = Registry()
        self.registry.registerInterface(IMLSUISettings)

    def test_controlpanel_view(self):
        """Validate that the configuration view is available."""
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='mls-controlpanel-ui',
        )
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_protected(self):
        """Validate that the configuration view needs authentication."""
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(
            Unauthorized,
            self.portal.restrictedTraverse,
            '@@mls-controlpanel-ui',
        )


class TestMLSUsageControlPanel(unittest.TestCase):
    """Validate usage control panel is available."""
    layer = INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        alsoProvides(self.portal.REQUEST, IPloneMLSLayer)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_controlpanel_view(self):
        """Validate that the configuration view is available."""
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='mls-controlpanel-usage',
        )
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_controlpanel_view_protected(self):
        """Validate that the configuration view needs authentication."""
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(
            Unauthorized,
            self.portal.restrictedTraverse,
            '@@mls-controlpanel-usage',
        )
