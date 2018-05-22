# -*- coding: utf-8 -*-
"""Upgrade ps.plone.mls to 1010 profile."""

from plone import api


PROFILE_ID = 'profile-ps.plone.mls.upgrades:1010'


def upgrade(context, logger=None):
    setup = api.portal.get_tool(name='portal_setup')
    setup.runAllImportStepsFromProfile(PROFILE_ID)
