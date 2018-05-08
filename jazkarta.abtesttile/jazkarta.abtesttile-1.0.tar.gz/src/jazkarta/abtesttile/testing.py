# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import jazkarta.abtesttile


class JazkartaAbtesttileLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=jazkarta.abtesttile)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'jazkarta.abtesttile:default')


JAZKARTA_ABTESTTILE_FIXTURE = JazkartaAbtesttileLayer()


JAZKARTA_ABTESTTILE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(JAZKARTA_ABTESTTILE_FIXTURE,),
    name='JazkartaAbtesttileLayer:IntegrationTesting',
)


JAZKARTA_ABTESTTILE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(JAZKARTA_ABTESTTILE_FIXTURE,),
    name='JazkartaAbtesttileLayer:FunctionalTesting',
)


JAZKARTA_ABTESTTILE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        JAZKARTA_ABTESTTILE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='JazkartaAbtesttileLayer:AcceptanceTesting',
)
