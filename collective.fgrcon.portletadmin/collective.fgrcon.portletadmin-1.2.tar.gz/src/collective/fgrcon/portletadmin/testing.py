# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.fgrcon.portletadmin


class CollectiveFgrconPortletadminLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.fgrcon.portletadmin)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.fgrcon.portletadmin:default')


COLLECTIVE_FGRCON_PORTLETADMIN_FIXTURE = CollectiveFgrconPortletadminLayer()


COLLECTIVE_FGRCON_PORTLETADMIN_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_FGRCON_PORTLETADMIN_FIXTURE,),
    name='CollectiveFgrconPortletadminLayer:IntegrationTesting'
)


COLLECTIVE_FGRCON_PORTLETADMIN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_FGRCON_PORTLETADMIN_FIXTURE,),
    name='CollectiveFgrconPortletadminLayer:FunctionalTesting'
)


COLLECTIVE_FGRCON_PORTLETADMIN_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_FGRCON_PORTLETADMIN_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveFgrconPortletadminLayer:AcceptanceTesting'
)
